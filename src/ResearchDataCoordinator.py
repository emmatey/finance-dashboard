import logging

from CommonQueries import CommonQueries
from enum import Enum
from helpers import TickerNotFoundError
from time import time


logger = logging.getLogger(__name__)

class TableLifetimes(Enum):
    """
    Specifies the age at which any given DB table should be updated.
    Done on a per-table basis because the 'research_api_helpers' are written to fetch and organize
    the data required to populate one record in one DB table each.

    table_name = lifetime_in_seconds
    """
    stock_splits = 604800  # 1 week
    historical_prices = 86400  # 24 hours
    financial_metrics = 43200  # 12 hours
    news = 3600  # 1 hour
    company_profile = 604800  # 1 week
    insider_trades = 86400  # 24 hours

class ResearchDataCoordinator(CommonQueries):
    """
    Handles updating of individual SQL tables of finance data based on the age
    of the records.
    """
    research_registry = {table_name: {'i': False, 'o': False, 'api': False, 'modules': []} for table_name in TableLifetimes.__members__}

    @classmethod
    def register_as_research(cls, table_name, i=False, o=False, api=False, modules=[]):
        # Specify in, out, or api with x=True to categorize functions.
        # Each table will generally have 3 related methods.
        def decorator(func):
            if table_name not in TableLifetimes.__members__:
                raise ValueError(f"Invalid table '{table_name}'. Must be in TableLifetimes enum.")
            if i:
                logger.debug(f"Registered {func} as db in function for {table_name}.")
                cls.research_registry[table_name]['i'] = func
            elif o:
                logger.debug(f"Registered {func} as db out function for {table_name}.")
                cls.research_registry[table_name]['o'] = func
            elif api:
                logger.debug(f"Registered {func} as api getter function for {table_name}.")
                cls.research_registry[table_name]['api'] = func
                if modules:
                    cls.research_registry[table_name]['modules'] = modules
            else:
                raise ValueError("Must specify function relation to table, i.e i = in, o = out, api = api adapter.")

            return func
        return decorator

    def create_research_fresh_report(self, symbol: str):
        """
        Check the age of stored data using a single optimized CTE query.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary mapping table names to freshness status.
            True = data is fresh, False = data is stale

        Raises:
            ValueError: If symbol not found in database

        Note:
            In benchmark testing on a mostly empty local DB, this method took 0.0009 seconds
            vs 0.002 seconds with the naive method of looping over individual queries to
            each table.
        """
        now = time()
        symbol = str(symbol).strip().upper()

        # Thank you to "https://www.datacamp.com/tutorial/cte-sql"
        query = self.select_query(
            """
            WITH target AS (
                SELECT id
                FROM symbols
                WHERE ticker = ?
            ),
            ss AS (
                SELECT max(unixepoch(last_updated)) as ts
                FROM stock_splits
                WHERE symbol_id = (SELECT id FROM target)
            ),
            hp AS (
                SELECT max(unixepoch(last_updated)) as ts
                FROM historical_prices
                WHERE symbol_id = (SELECT id FROM target)
            ),
            fm AS (
                SELECT unixepoch(last_updated) as ts
                FROM financial_metrics
                WHERE symbol_id = (SELECT id FROM target)
            ),
            n AS (
                SELECT max(unixepoch(timeInserted)) as ts
                FROM news
                JOIN news_symbols AS ns
                ON news.id = ns.news_id
                WHERE ns.symbol_id = (SELECT id FROM target)
            ),
            cp as (
                SELECT unixepoch(last_updated) as ts
                FROM company_profile
                WHERE symbol_id = (SELECT id FROM target)
            ),
            it as (
                SELECT max(unixepoch(last_updated)) as ts
                FROM insider_trades
                WHERE symbol_id = (SELECT id FROM target)
            )

            SELECT
                (SELECT ts FROM ss) AS stock_splits,
                (SELECT ts FROM hp) AS historical_prices,
                (SELECT ts FROM fm) AS financial_metrics,
                (SELECT ts FROM n) AS news,
                (SELECT ts FROM cp) AS company_profile,
                (SELECT ts FROM it) AS insider_trades
            """, (symbol, ))

        if not query:
            logger.error(f"Symbol {symbol} not found in database")
            query = [{}]

        res = query[0]
        fresh_report: dict[str, bool | str] = {"symbol": symbol}

        for name, create_time in res.items():
            if name in TableLifetimes.__members__:
                if not isinstance(create_time, (int, float)):
                    logger.debug(f"Data for {name} is missing/None. Marking as stale.")
                    create_time = 0
                if TableLifetimes[name].value > (now - create_time):
                    logger.debug(f"Data for {name} is fresh. Age={now - create_time} Threshold={TableLifetimes[name].value}, Ticker={symbol}")
                    fresh_report[name] = True
                else:
                    logger.debug(f"Data for {name} is stale. Age={now - create_time} Threshold={TableLifetimes[name].value}, Ticker={symbol}")
                    fresh_report[name] = False
            else:
                logger.warning(f"Database returned column '{name}', but it is not tracked in TableLifetimes Enum.")

        return fresh_report

    def research_data_update_orchestrator(self, fresh_report: dict[str, bool | str], yqs_instance=None, db_io_instance=None):
        """
        Parse a freshness report and update stale data for a single company.

        Collects all required Yahoo Finance modules for stale tables, makes a single
        API call, then dispatches to the appropriate setter functions via the registry.

        Args:
            fresh_report: Dict mapping table names to freshness status.
                          Must contain a 'symbol' key with the ticker string.
                          True = fresh (skip), False = stale (update).
                          Format: {'symbol': <str>, 'financial_metrics': False, ...}
            yqs_instance: YahooQueryService instance for API calls.
            db_io_instance: APIDataIO instance for database writes.

        Raises:
            AssertionError: If 'symbol' key in fresh_report is not a string.
            RuntimeError: If fresh_report contains no symbol, if the API fails to
                          return modules, or if a table has incomplete registry
                          registration (missing api or in function).
            ValueError: If yqs_instance or db_io_instance are not provided.
            TickerNotFoundError: If the ticker symbol is not found on Yahoo Finance.
            Exception: Re-raises any exception that occurs during individual table
                       updates after logging the error.
        """

        symbol = fresh_report.get('symbol')
        assert isinstance(symbol, str)
        if not symbol:
            logger.info(f"fresh_report invalid, no company name found. {fresh_report}")
            raise RuntimeError("Malformed fresh_report, no symbol found.")

        if not yqs_instance or not db_io_instance:
            logger.info("research_data_update_orchestrator function requires YahooQueryService and MarketDataIO instances.")
            raise ValueError("research_data_update_orchestrator function requires YahooQueryService and MarketDataIO instances.")

        # Collect list of modules required by updater functions who are associated with 'stale' data.
        modules_set = set()
        for table, status in fresh_report.items():
            if status is False:
                required_modules = self.research_registry[table].get('modules')
                if required_modules:
                    for m in required_modules:
                        modules_set.add(m)

        # Always get price if anything is stale so upsert_symbol can be called.
        modules_set.add("price")

        # Call api once for all required modules.
        modules = {}
        logger.info(f"Fetching {len(modules_set)} modules for {symbol}")
        modules = yqs_instance.yq_ticker_fetch_modules(symbol, list(modules_set))
        if isinstance(modules.get(symbol), str) and "Quote not found" in modules[symbol]:
            logger.error(f"Ticker {symbol} not found on Yahoo Finance.")
            raise TickerNotFoundError(f"Ticker {symbol} not found on Yahoo Finance.")
        if not modules:
            logger.error(f"API failed to fetch modules for {symbol}")
            raise RuntimeError(f"API failed to fetch modules for {symbol}")
        else:
            # Upsert symbol using already-fetched modules (no extra API call)
            db_io_instance.upsert_symbols(modules)

        # Call refresh functions for stale db tables
        for table, status in fresh_report.items():
            # Fresh report has a default k:v pair "fresh_report = {"symbol": symbol}" key is literally the string "symbol" skipping here.
            if table == "symbol":
                continue
            if status is False:
                try:
                    # Fetch functions from registry
                    api_func = self.research_registry[table]['api']
                    in_func = self.research_registry[table]['i']
                    modules_required = self.research_registry[table]['modules']

                    if not api_func or not in_func:
                        logger.error(f"Incomplete registry registration for table '{table}'")
                        raise RuntimeError(f"Incomplete registry registration for table '{table}'")
                    if modules_required:
                        data = api_func(yqs_instance, modules)
                        in_func(db_io_instance, data)
                    else:
                        data = api_func(yqs_instance, symbol)
                        in_func(db_io_instance, data)

                except Exception as e:
                    logger.error(f"Failed to update {table} for {symbol}: {e}")
                    raise 

    def update_table_subset(self,
                            ticker:str,
                            tables_to_update: list[str],
                            yqs_instance=None,
                            db_io_instance=None
                            ) -> None:
        """
        Requests to yahooquery for data in tables_to_update param assocaited with ticker param.

        tables_to_update valid options: stock_splits, historical_prices, financial_metrics, 
                                news, company_profile, insider_trades
        """
        if not yqs_instance or not db_io_instance:
            raise ValueError("research_data_update_orchestrator function requires YahooQueryService and APIDataIO instances.")

        for table_name in tables_to_update:
            if table_name not in TableLifetimes.__members__:
                    raise ValueError(f"Invalid table '{table_name}'. Must be in TableLifetimes enum.")
            
        fresh_report = self.create_research_fresh_report(symbol=ticker)
        for table in list(fresh_report.keys()):
            if table not in ["symbol"] + tables_to_update:
                fresh_report[table] = True
        self.research_data_update_orchestrator(
            fresh_report=fresh_report,
            yqs_instance=yqs_instance,
            db_io_instance=db_io_instance
        )
    
    def get_research_data(self,
                          ticker: list[str] | str,
                          tables_to_get: list[str]=["stock_splits", "historical_prices", "financial_metrics", "news", "company_profile", "insider_trades"],
                          db_io_instance=None
                          ) -> dict[str, list[dict]]:
        """
        Pulls a subset of research data from the database. 
        Will not trigger updates, assumes this has been done elsewhere.

        Args:
            - ticker: company or companies to fetch data for.
            - "tables_to_get" valid options: stock_splits, historical_prices, financial_metrics, 
                                    news, company_profile, insider_trades
            - db_io_instance: APIDataIO() class instance.
        
        Returns:
            {
                table_name: [{}, ...],
                ...
            }
        """
        if not db_io_instance:
            raise ValueError("get_research_data function requires APIDataIO instance.")
        VALID_OPTIONS = "stock_splits, historical_prices, financial_metrics, news, company_profile, insider_trades"

        # normalize input type
        if not isinstance(tables_to_get, list):
            raise ValueError(f"tables_to_get argument must be a list of strings is {type(tables_to_get)}... ")
        if not all(isinstance(i, str) for i in tables_to_get):
            raise ValueError(f"tables_to_get argument must be a list of strings...")
        
        if isinstance(ticker, str):
            ticker = [ticker.strip().upper()]
        elif isinstance(ticker, list):
            if not all(isinstance(i, str) for i in ticker):
                raise ValueError(f"Ticker argument must be a string or a list of strings...")
            else:
                ticker = [i.strip().upper() for i in ticker]
        else:
            raise ValueError(f"Ticker argument must be a string or a list of strings. is {type(ticker)}...")
            
        # fetch functions associated with param
        tables = (i.lower() for i in tables_to_get)
        results = {}
        invalid_params = []
        missing_out_func = []
        for table in tables:
            table_funcs = self.research_registry.get(table, None)
            if not table_funcs: 
                invalid_params.append(table)
                continue
            
            out_func = table_funcs.get("o", None)
            if out_func is None:
                missing_out_func.append(table)
            else:
                try:
                    res = out_func(db_io_instance, ticker)
                except Exception:
                    raise

                results[table] = res

        # log not found funcitons
        if invalid_params:
            logger.warning(f"Paramaters {str(invalid_params)} are invalid. Valid options are {VALID_OPTIONS}")

        if missing_out_func:
            logger.warning(f"Paramaters {str(missing_out_func)} have no registered 'out' function. Cannot retreive info from db.")

        # return result 
        return results
  