import logging

from CommonQueries import CommonQueries
from enum import Enum
from helpers import TickerNotFoundError
from time import time, strftime, gmtime


logger = logging.getLogger(__name__)

class TableLifetimes(Enum):
    """
    Specifies the age at which any given DB table should be updated.
    Done on a per-table basis because the 'research_api_helpers' are written to fetch and organize
    the data required to populate one record in one DB table each.

    table_name = lifetime_in_seconds
    """
    stock_splits = 86400  # 24 hours
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
    research_registry = {table_name: {'i': False, 'o': False, 'api': False, 'post': False, 'modules': []} for table_name in TableLifetimes.__members__}

    @classmethod
    def register_as_research(cls, table_name, i=False, o=False, api=False, post=False, modules=[]):
        """
        Decorator for registering functions into the research data pipeline registry.

        Each table in TableLifetimes can have up to four registered functions:

            api: Fetches raw data from Yahoo Finance and parses it into a
                 structured format for database insertion. Receives either a
                 yq modules payload or a ticker string depending on whether
                 'modules' is specified.

            i:   Writes parsed data to the database. Receives a db_io_instance
                 and the output of the table's registered api function.

            o:   Reads and returns data from the database for a given ticker.
                 Receives a db_io_instance and a ticker list.

            post: Runs after all i functions complete, regardless of which tables
                  were updated in a given orchestrator run. Intended for derived
                  metrics that are computed from already-stored data rather than
                  fetched directly from an API (e.g. a sentiment score derived
                  from insider_trades rows). Receives a db_io_instance only.

        Args:
            table_name: Must be a valid TableLifetimes member.
            i:       Register as database write function.
            o:       Register as database read function.
            api:     Register as API fetch/parse function.
            post:    Register as post-processing function for derived metrics.
            modules: Yahoo Finance modules required by the api function.
        """
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
            elif post:
                logger.debug(f"Registered {func} as post-processing function for {table_name}.")
                cls.research_registry[table_name]['post'] = func
            else:
                raise ValueError("Must specify function relation to table, i.e i = in, o = out, api = api, post = post-processing.")
            return func
        return decorator

    def create_research_fresh_report(self, symbol: str):
        """
        Check the age of stored data associated with the given symbol/ticker.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary mapping table names to freshness status.
                True = data is fresh,
                False = data is stale
        """
        fresh_report: dict[str, bool | str] = {table: False for table in TableLifetimes.__members__}
        fresh_report["symbol"] = symbol
        symbol = str(symbol).strip().upper()
        symbol_id = self.get_symbol_id(symbol)
        if symbol_id is None:
            logger.debug(f"Symbol {symbol} not found in DB")
            return fresh_report

        fresh_sql = """
        SELECT table_name, unixepoch(last_updated) AS last_updated
        FROM fresh_report
        WHERE symbol_id = ?
        """
        raw_ages = {}
        rows = self.select_query(fresh_sql, (symbol_id,))
        for row in rows:
            table_name = row.get("table_name", "")
            last_updated = row.get("last_updated", 0)
            if table_name:
                raw_ages[table_name] = last_updated

        now = time()
        for name, create_time in raw_ages.items():
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
        After all updates complete, runs any registered post-processing functions
        unconditionally — these compute derived metrics from already-stored data.

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
        def _claim_fresh_report(fresh_report):
            """
            Write current UTC timestamp to fresh_report table for all stale tables.
            Acts as a job claim — blocks parallel requests from doing the same work.
            Returns the list of table names claimed, for use in rollback.
            """
            now = strftime('%Y-%m-%d %H:%M:%S', gmtime())
            symbol_id = self.get_symbol_id(fresh_report["symbol"])
            tables_to_claim = [table for table, fresh in fresh_report.items() if fresh is False]
            if not tables_to_claim:
                return []
            fresh_sql = """
            INSERT INTO fresh_report (symbol_id, table_name, last_updated)
            VALUES (?, ?, ?)
            ON CONFLICT(symbol_id, table_name)
            DO UPDATE SET last_updated = excluded.last_updated
            """
            table_tuples = [(symbol_id, table, now) for table in tables_to_claim]
            self.bulk_query(fresh_sql, table_tuples)
            return tables_to_claim

        def _rollback_fresh_report(symbol, claimed_tables):
            """
            Delete claimed rows on failure so the next request will retry.
            """
            if not claimed_tables:
                return
            symbol_id = self.get_symbol_id(symbol)
            placeholders = ", ".join("?" for _ in claimed_tables)
            rollback_sql = f"""
            DELETE FROM fresh_report
            WHERE symbol_id = ?
            AND table_name IN ({placeholders})
            """
            self.modify_query(rollback_sql, (symbol_id, *claimed_tables))
            logger.info(f"Rolled back fresh_report claim for {symbol}: {claimed_tables}")

        # Validate before touching the DB
        symbol = fresh_report.get('symbol')
        assert isinstance(symbol, str)
        if not symbol:
            logger.info(f"fresh_report invalid, no company name found. {fresh_report}")
            raise RuntimeError("Malformed fresh_report, no symbol found.")
        if not yqs_instance or not db_io_instance:
            raise ValueError("research_data_update_orchestrator requires YahooQueryService and APIDataIO instances.")

        # Claim the job — write now to block duplicate requests
        claimed_tables = _claim_fresh_report(fresh_report=fresh_report)
        if not claimed_tables:
            logger.debug(f"Nothing stale for {symbol}, skipping.")
            return

        try:
            # Collect modules required by stale tables
            modules_set = set()
            for table, status in fresh_report.items():
                if status is False:
                    required_modules = self.research_registry.get(table, {}).get('modules')
                    if required_modules:
                        for m in required_modules:
                            modules_set.add(m)

            # Always get price if anything is stale so upsert_symbol can be called.
            modules_set.add("price")

            # Call API once for all required modules.
            logger.info(f"Fetching {len(modules_set)} modules for {symbol}... {modules_set}")
            modules = yqs_instance.yq_ticker_fetch_modules(symbol, list(modules_set))
            if isinstance(modules.get(symbol), str) and "Quote not found" in modules[symbol]:
                logger.error(f"Ticker {symbol} not found on Yahoo Finance.")
                raise TickerNotFoundError(f"Ticker {symbol} not found on Yahoo Finance.")
            if not modules:
                logger.error(f"API failed to fetch modules for {symbol}")
                raise RuntimeError(f"API failed to fetch modules for {symbol}")

            # Upsert symbol using already-fetched modules (no extra API call)
            db_io_instance.upsert_symbols(modules)

            # Call refresh functions for stale tables
            any_updated = False
            for table, status in fresh_report.items():
                # fresh_report always contains {"symbol": <str>} — skip it
                if table == "symbol":
                    continue
                if status is False:
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

                    any_updated = True

            # Run post-processing unconditionally if anything was updated.
            # These compute derived metrics from already-stored data.
            if any_updated:
                # Write true completion time now that work is done
                _claim_fresh_report(fresh_report=fresh_report)
                for table, funcs in self.research_registry.items():
                    post_func = funcs.get('post')
                    if post_func:
                        try:
                            logger.debug(f"Running post-processing for {table}.")
                            post_func(self, symbol)
                        except Exception as e:
                            logger.error(f"Post-processing failed for {table}, symbol {symbol}: {e}")
                            raise

        except Exception:
            _rollback_fresh_report(symbol=symbol, claimed_tables=claimed_tables)
            raise

    def update_research_data_subset(self,
                            ticker: str,
                            tables_to_update: list[str],
                            yqs_instance=None,
                            db_io_instance=None
                            ) -> None:
        """
        Requests to yahooquery for data in tables_to_update param associated with ticker param.

        tables_to_update valid options: stock_splits, historical_prices, financial_metrics,
                                news, company_profile, insider_trades
        """
        if not yqs_instance or not db_io_instance:
            raise ValueError("update_research_data_subset requires YahooQueryService and APIDataIO instances.")

        for table_name in tables_to_update:
            if table_name not in TableLifetimes.__members__:
                raise ValueError(f"Invalid table '{table_name}'. Must be in TableLifetimes enum.")

        # Fresh report checks status of relevant tables.
        # All others are forced to True/Fresh to skip fetching.
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
                          tables_to_get: list[str]=["symbols", "stock_splits", "historical_prices", "financial_metrics", "news", "company_profile", "insider_trades"],
                          db_io_instance=None
                          ) -> dict[str, list[dict]]:
        """
        Pulls a subset of research data from the database.
        Will not trigger updates, assumes this has been done elsewhere.

        Args:
            - ticker: company or companies to fetch data for.
            - tables_to_get valid options: stock_splits, historical_prices, financial_metrics,
                                    news, company_profile, insider_trades
            - db_io_instance: APIDataIO() class instance.

        Returns:
            {
                table_name: [{}, ...],
                ...
            }
        """
        if not db_io_instance:
            raise ValueError("get_research_data requires APIDataIO instance.")
        VALID_OPTIONS = ['symbols', 'stock_splits', 'historical_prices', 'financial_metrics', 'news', 'company_profile', 'insider_trades']

        if not isinstance(tables_to_get, list):
            raise ValueError(f"tables_to_get must be a list of strings, got {type(tables_to_get)}")
        if not all(isinstance(i, str) for i in tables_to_get):
            raise ValueError("tables_to_get must be a list of strings.")
        for i in tables_to_get:
            if i not in VALID_OPTIONS:
                raise ValueError(f"{i} not a valid table, options are {VALID_OPTIONS}...")

        if isinstance(ticker, str):
            ticker = [ticker.strip().upper()]
        elif isinstance(ticker, list):
            if not all(isinstance(i, str) for i in ticker):
                raise ValueError("Ticker must be a string or list of strings.")
            ticker = [i.strip().upper() for i in ticker]
        else:
            raise ValueError(f"Ticker must be a string or list of strings, got {type(ticker)}.")

        tables = (i.lower() for i in tables_to_get)
        results = {}
        invalid_params = []
        missing_out_func = []

        for table in tables:
            table_funcs = self.research_registry.get(table)
            if not table_funcs:
                invalid_params.append(table)
                continue

            out_func = table_funcs.get("o")
            if out_func is None:
                missing_out_func.append(table)
            else:
                try:
                    results[table] = out_func(db_io_instance, ticker)
                except Exception:
                    raise

        if invalid_params:
            logger.warning(f"Invalid params {invalid_params}. Valid options: {VALID_OPTIONS}")
        if missing_out_func:
            logger.warning(f"No registered 'out' function for {missing_out_func}.")

        return results