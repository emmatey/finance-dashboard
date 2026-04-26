import logging

from DbManager import DbManager
from ResearchDataCoordinator import ResearchDataCoordinator
from typing import Any, Dict, List, Optional, Tuple, Union


logger = logging.getLogger(__name__)


class APIDataIO(DbManager):
    """
    CRUD type operations on data from Yahoo API.

    SyncManager > YahooAPIClient > 'Setters'
    'Getters' > ReportManager

    Used by SyncManager to refresh stale external data.
    Used by ReportManager to fetch information to display on UI.

    Standard Format: List of Dicts for Multiple Records
    For Single Record: Dict or None
    """

    def upsert_symbols(self, modules_dict: dict):
        """
        Upsert symbols within supplied price module in database's 'symbols' table.

        Args:
            module dict from YahooQuery containing the 'price' module.
            https://yahooquery.dpguthrie.com/guide/ticker/modules/#price
            eg {'symbol':{
                   'price': {label: data},
                   'defaultKeyStatistics: {label: data},
                    ...
                }
        """
        sql = """
        INSERT INTO symbols (quote_type, exchange, ticker, company_name, last_price, last_updated)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(ticker) DO UPDATE SET
            quote_type = excluded.quote_type,
            exchange = excluded.exchange,
            company_name = excluded.company_name,
            last_price = excluded.last_price,
            last_updated = CURRENT_TIMESTAMP
        """
        symbols_tuples: list[tuple] = []
        for symbol, modules in modules_dict.items():
            if not isinstance(modules, dict):
                logger.error(f"Malformed module for {symbol}...skipping")
                logger.error(modules)
                continue

            price_module = modules.get('price')
            if not isinstance(price_module, dict):
                logger.error(f"Malformed module for {symbol}...skipping")
                logger.error(modules)
                continue
            
            if price_module:
                quote_type = price_module.get('quoteType', 'UNKNOWN')
                if quote_type == 'UNKNOWN':
                    logger.debug(f"Missing quoteType for {symbol}, price_module keys: {list(price_module.keys())}")
                exchange = price_module.get('exchangeName')
                if not exchange:
                    exchange = price_module.get("exchange", "UNKNOWN")
                company_name = (
                    price_module.get('longName') or 
                    price_module.get('shortName') or 
                    symbol.upper()
                )
                last_price = price_module.get('regularMarketPrice')
                if not last_price:
                    continue
                symbols_tuples.append(tuple([quote_type, exchange, symbol, company_name, last_price]))

            else:
                logger.warning(f"'price' module not found for {symbol}.")

        self.bulk_query(sql, symbols_tuples)
        
    ### SETTERS ###

    @ResearchDataCoordinator.register_as_research('stock_splits', i=True)
    def set_stock_splits(self, stock_split_data: List[Tuple]) -> None:
        """
        (ticker, datetime, ratio)
        [(datetime.date(1972, 6, 16), 2.0, 'MMM'), (datetime.date(1987, 6, 16), 2.0, 'MMM'),]
        DbManager.bulk_query() handles logging and exceptions and transaction control
        """
        # yq_ticker_stock_splits() method returns [] on errors.
        if not stock_split_data or not isinstance(stock_split_data[0], tuple):
            logger.warning(f"No data recieved param:{stock_split_data}")
            return None

        sql = """
        INSERT INTO stock_splits (symbol_id, split_date, split_ratio)
        SELECT id, ?, ?
        FROM symbols
        WHERE ticker = ?
        ON CONFLICT(symbol_id, split_date)
        DO UPDATE SET
            split_ratio = excluded.split_ratio,
            last_updated = CURRENT_TIMESTAMP
        """

        self.bulk_query(sql, stock_split_data)

    @ResearchDataCoordinator.register_as_research('historical_prices', i=True)
    def set_historical_prices(self, price_data):
        """
        price_data eg [(datetime.date(2026, 2, 24), 166.46000671, 2468500, 'MMM')]
        DbManager.bulk_query() handles logging and exceptions and transaction control
        """
        # yq_ticker_historical_prices() method returns None on errors.
        if not price_data or not isinstance(price_data[0], tuple):
            logger.warning(f"No data recieved param:{price_data}")
            return None

        sql = """
        INSERT INTO historical_prices (symbol_id, price_timestamp, adjclose, trade_volume)
        SELECT id, ?, ?, ?
        FROM symbols
        WHERE ticker = ?
        ON CONFLICT(symbol_id, price_timestamp)
        DO UPDATE SET
            last_updated = CURRENT_TIMESTAMP,
            adjclose = CASE
                WHEN historical_prices.adjclose != excluded.adjclose THEN excluded.adjclose
                ELSE historical_prices.adjclose
            END,
            trade_volume = CASE
                WHEN historical_prices.adjclose != excluded.adjclose THEN excluded.trade_volume
                ELSE historical_prices.trade_volume
            END
        """

        self.bulk_query(sql, price_data)

    @ResearchDataCoordinator.register_as_research('financial_metrics', i=True)
    def set_financial_metrics(
        self,
        metrics: Dict[str, Dict[str, Optional[Union[float, str, int]]]],
        from_screeners = False
    ) -> None:
        """
        Insert or update financial metrics for one or more companies in the database.

        Dynamically builds an UPSERT query based on the metrics dictionary structure.
        If a symbol_id already exists, updates all fields and refreshes last_updated timestamp.

        Args:
            metrics: Dictionary mapping ticker symbols to their financial metrics. From the YahooQueryService class
                    Format: {
                        'AAPL': {
                            'market_open': 150.25,
                            'prev_close': 149.50,
                            'market_cap': 2500000000000,
                            'beta': 1.2,
                            'eps': 6.15,
                            'trailing_pe': 24.4,
                            'forward_pe': 22.1,
                            'profit_margin': 0.25,
                            'dividend_yield': 0.005,
                            'fifty_two_week_high': 180.0,
                            'fifty_two_week_low': 120.0,
                            'rating': 'buy',
                            'target_price': 175.0,
                            'analyst_count': 45,
                            'current_ratio': 1.5,
                            'debt_to_equity': 0.8
                        },
                        'MSFT': { ... }
                    }

                    All metric values are Optional (can be None for missing data).
                    Supports single or multiple tickers.
        """
        if not metrics:
            """
            Data reaches this function via YahooQueryService.yq_ticker_get_modules > YahooQueryService.get_financial_metrics
            get_modules returns {} on api errors
            get_financial_metrics returns {} if get_modules return value is falsy.
            Logged up-stream if api has un-expected return value resulting in sending {}'s down the chain.
            """
            logger.warning("financial_metrics updated aborted. No data found.")
            return None

        table_cols = sorted({key for data in metrics.values() for key in data})
        table_cols_str = ", ".join(table_cols)
        placeholders = ", ".join(["?" for i in table_cols])
        excluded_cols_str = ", ".join(f"{col}=excluded.{col}" for col in table_cols)

        data_tuples = []
        for symbol, data in metrics.items():
            buffer = [data.get(col) for col in table_cols]
            buffer.append(symbol)  # ticker for WHERE clause
            data_tuples.append(tuple(buffer))

        update_time = ""
        if from_screeners == False:
            # Dont update timestamp on incomplete data from screeners.
            update_time = "last_updated=CURRENT_TIMESTAMP,"
        sql = f"""
            INSERT INTO financial_metrics (symbol_id, {table_cols_str})
            SELECT id, {placeholders}
            FROM symbols
            WHERE ticker = ?
            ON CONFLICT(symbol_id)
            DO UPDATE SET
            {update_time} {excluded_cols_str}
            """

        self.bulk_query(sql, data_tuples)

    @ResearchDataCoordinator.register_as_research('news', i=True)
    def set_news(self, news_data: List[Dict[str, Any]]) -> None:
        """
        Insert or update news articles and their relationships to stock symbols.

        Handles the many-to-many relationship between news articles and symbols
        by inserting into both the 'news' table and the 'news_symbols' junction table.
        Stories are associated only with symbols that exist in the database.

        Args:
            news_data: List of news article dictionaries from yq_search_fetch_news()
                      Format: [
                          {
                              'uuid': 'abc-123-def',
                              'title': 'Steve Jobs Returns From the Dead!',
                              'publisher': 'Reuters',
                              'link': 'https://example.com/article',
                              'providerPublishTime': 1234567890,
                              'thumbnail': 'https://example.com/image.jpg',
                              'relatedTickers': ['AAPL', 'MSFT', 'GOOGL']
                          },
                          ...
                      ]

        Returns:
            None (side effects: updates news and news_symbols tables)

        Raises:
            Exception: Any database errors from bulk_query() or simple_query()

        Database Tables Modified:
            - news: Stores article metadata
            - news_symbols: Junction table linking news articles to stock symbols

        """
        if not news_data:
            return

        # Insert news stories.
        table_cols = sorted({key for dict in news_data for key in dict})
        table_cols_str = ", ".join((col for col in table_cols if col != "relatedTickers"))
        placeholders = ", ".join(["?" for i in table_cols if i != "relatedTickers"])
        excluded_cols_str = ", ".join(
            f"{col}=excluded.{col}" for col in table_cols if col != "relatedTickers" and col != "uuid")

        news_tuples = []
        for story in news_data:
            buffer = []
            # Tuples data must keep the same order as table_cols
            ordered_story = [i for i in table_cols if i != "relatedTickers"]
            for i in ordered_story:
                buffer.append(story.get(i))
            news_tuples.append(tuple(buffer))

        insert_news_sql = f"""
        INSERT INTO news ({table_cols_str})
        VALUES ({placeholders})
        ON CONFLICT(uuid)
        DO UPDATE SET
        timeInserted=CURRENT_TIMESTAMP, {excluded_cols_str}
        """
        self.bulk_query(insert_news_sql, news_tuples)

        # Associate news stories to ticker symbols
        related_uuids = {}
        for story in news_data:
            related_uuids[story.get('uuid')] = story.get('relatedTickers')
        uuid_set = {i for i in related_uuids}
        uuid_placeholders = ", ".join(["?" for _ in uuid_set])
        ticker_set = {ticker for v in related_uuids.values() if v for ticker in v}
        ticker_placeholders = ", ".join(["?" for _ in ticker_set])

        # Find news id for associated uuid
        uuid_sql = f"""
        SELECT uuid, id AS news_id
        FROM news
        WHERE uuid IN ({uuid_placeholders})
        """
        uuid_rows = self.select_query(uuid_sql, tuple(uuid_set))
        uuid_cipher = {i.get('uuid'): i.get('news_id') for i in uuid_rows}

        # Find symbol id for associated ticker
        ticker_sql = f"""
        SELECT ticker, id as symbol_id
        FROM symbols
        WHERE ticker in ({ticker_placeholders})
        """
        ticker_rows = self.select_query(ticker_sql, tuple(ticker_set))
        ticker_cipher = {i.get('ticker'): i.get('symbol_id') for i in ticker_rows}

        # Add basic info about a ticker into the db if it doesn't already exist to allow stories to be linked to it.
        known_tickers = set(ticker_cipher.keys())
        unknown_tickers = ticker_set - known_tickers
        if unknown_tickers:
            minimal_sql = """
            INSERT INTO symbols (quote_type, ticker, company_name)
            VALUES ('UNKNOWN', ?, ?)
            ON CONFLICT(ticker) DO NOTHING
            """
            self.bulk_query(minimal_sql, [(t, t) for t in unknown_tickers])
            # re-run ticker query to get new ids
            ticker_rows = self.select_query(ticker_sql, tuple(ticker_set))
            ticker_cipher = {i.get('ticker'): i.get('symbol_id') for i in ticker_rows}

        # go from {uuid: [ticker]} to {news_id: [ticker_id]}
        translated_related_uuids = {}
        for uuid, tickers in related_uuids.items():
            buffer = []
            if not tickers:
                continue
            for ticker in tickers:
                translated = ticker_cipher.get(ticker)
                if translated:
                    buffer.append(translated)
            news_id = uuid_cipher.get(uuid)
            if news_id:
                translated_related_uuids[news_id] = buffer

        # Insert into 'news_symbols'
        news_symbols_tuples = []
        for news_id, ticker_ids in translated_related_uuids.items():
            for ticker_id in ticker_ids:
                news_symbols_tuples.append((news_id, ticker_id))
        news_symbols_sql = f"""
        INSERT INTO news_symbols (news_id, symbol_id)
        VALUES (?, ?)
        ON CONFLICT(news_id, symbol_id)
        DO NOTHING
        """
        self.bulk_query(news_symbols_sql, news_symbols_tuples)

    @ResearchDataCoordinator.register_as_research('company_profile', i=True)
    def set_company_profile(
        self,
        company_overview: Dict[str, Dict[str, Union[str, int]]]
    ) -> None:
        """
        Insert or update company profile information for one or more companies.

        Dynamically builds an UPSERT query based on the company_overview dictionary structure.
        If a symbol_id already exists, updates all fields and refreshes last_updated timestamp.

        Args:
            company_overview: Dictionary mapping ticker symbols to their company profile data.
                             Format: {
                                 'AAPL': {
                                     'company_desc': 'Apple Inc. designs, manufactures...',
                                     'employee_count': 164000,
                                     'industry': 'Consumer Electronics',
                                     'sector': 'Industrials',
                                     'website': 'https://www.apple.com'
                                 },
                                 'MSFT': {
                                     'company_desc': 'Microsoft Corporation develops...',
                                     'employee_count': 221000,
                                     'industry': 'Software—Infrastructure',
                                     'sector': 'Industrials",
                                     'website': 'https://www.microsoft.com'
                                 }
                             }

                             Supports single or multiple tickers.

        Returns:
            None (side effect: database is updated)

        Raises:
            Exception: Any database errors from bulk_query() (logged and re-raised)
        """
        if not company_overview:
            logger.warning(
                "set_company_profile aborted: empty company_overview dict")
            return None

        table_cols = sorted({key for dict in company_overview.values() for key in dict})
        table_cols_str = ", ".join((col for col in table_cols))
        placeholders = ", ".join(["?" for i in table_cols])
        excluded_cols_str = ", ".join(
            f"{col}=excluded.{col}" for col in table_cols)

        summary_tuples = []
        for symbol, data in company_overview.items():
            buffer = []
            # Tuples data must keep the same order as table_cols
            for col in table_cols:
                buffer.append(data.get(col))
            buffer.append(symbol)  # For WHERE clause
            summary_tuples.append(tuple(buffer))

        sql = f"""
        INSERT INTO company_profile (symbol_id, {table_cols_str})
        SELECT s.id, {placeholders}
        FROM symbols AS s
        WHERE ticker = ?
        ON CONFLICT(symbol_id)
        DO UPDATE SET
        last_updated=CURRENT_TIMESTAMP, {excluded_cols_str}
        """
        self.bulk_query(sql, summary_tuples)

    @ResearchDataCoordinator.register_as_research('insider_trades', i=True)
    def set_insider_trades(self, trade_data: dict):
        """
        param:
        {symbol: [
            {
                startDate: Transaction date (string: 'YYYY-MM-DD')
                shares: Number of shares traded
                value: Transaction value
                filerName: Name of insider
                filerRelation: Insider's relationship to company
                transactionText: Description of transaction type
            },
        """
        if not trade_data:
            logger.warning("set_insider_trades aborted: empty trade_data dict")
            return None

        # Filter out symbols with empty transaction lists
        trade_data = {k: v for k, v in trade_data.items() if v}
        if not trade_data:
            logger.warning("set_insider_trades aborted: no transactions found for any symbol")
            return None

        table_cols = sorted({key for tx_list in trade_data.values()
                            for tx in tx_list for key in tx})
        table_cols_str = ", ".join((col for col in table_cols))
        placeholders = ", ".join(["?" for i in table_cols])

        insider_tuples = []
        for symbol, tx_list in trade_data.items():
            for tx in tx_list:
                buffer = []
                # Tuples data must keep the same order as table_cols
                for col in table_cols:
                    buffer.append(tx.get(col))
                buffer.append(symbol)  # For WHERE clause
                insider_tuples.append(tuple(buffer))

        sql = f"""
        INSERT INTO insider_trades (symbol_id, {table_cols_str})
        SELECT s.id, {placeholders}
        FROM symbols AS s
        WHERE ticker = ?
        ON CONFLICT(symbol_id, transaction_date, filer_name, shares)
        DO NOTHING
        """
        self.bulk_query(sql, insider_tuples)

    def set_screeners_metadata(self, screener_metadata: Dict[str, List[str]]) -> None:
        """
        Insert screener metadata to db.
        
        Example:
                 # Full pipeline
            >>> raw = yqs.yq_screener_get_screeners(['day_gainers', 'most_actives'], count=n)
            >>> filtered = yqs._filter_screener_data(raw)
            >>> volume_swings = yqs.get_relative_volumes(filtered)
            >>> filtered.update(volume_swings)
            >>> screener_data = yqs.extract_screener_data_for_db(filtered)
            >>> db_io.set_screeners(screener_data, yqs)
            INFO: Inserted 50 fresh screener results across 2 screeners
        """
        # Clear old screener data
        self.modify_query("DELETE FROM screener_results")

        # Insert fresh screener results
        sql = """
            INSERT INTO screener_results (symbol_id, screener_name, rank)
            SELECT s.id, ?, ?
            FROM symbols AS s
            WHERE ticker = ?
        """
        screener_tuples: List[Tuple[str, int, str]] = []
        for screener_name, tickers in screener_metadata.items():
            for rank, ticker in enumerate(tickers, start=1):
                screener_tuples.append((screener_name, rank, ticker))

        self.bulk_query(sql, screener_tuples)
        logger.info(f"Inserted {len(screener_tuples)} screener results across {len(screener_metadata)} screeners")

    ### GETTERS ###

    @ResearchDataCoordinator.register_as_research('historical_prices', o=True)
    def get_historical_prices(self, symbols):
        """
        list of dicts
        returns
        [{'ticker': 'MMM', 'price': 69.42, 'timestamp': 1771891200, 'volume': 2468500}]
        """
        if not symbols:
            return []
        symbols = tuple([symbol.upper() for symbol in symbols])
        placeholders = ", ".join(['?' for _ in symbols])

        sql = f"""
        SELECT s.ticker, adjclose as price, unixepoch(hp.price_timestamp) as timestamp, hp.trade_volume as volume
        FROM historical_prices AS hp
        JOIN symbols AS s ON s.id = hp.symbol_id
        WHERE s.ticker IN ({placeholders})
        """

        return self.select_query(sql, symbols)

    @ResearchDataCoordinator.register_as_research('financial_metrics', o=True)
    def get_financial_metrics(self, symbols: list[str] | str) -> list[dict]:
        """
        Retrieve financial metrics for one or more symbols.
        
        Args:
            symbols: Single ticker string or list of tickers
        
        Returns:
            List of dicts.
            Empty list if no symbols provided or none found.
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        if not symbols:
            return []
        
        symbols_upper: list[str] = [symbol.upper() for symbol in symbols]
        placeholders = ", ".join(['?' for _ in symbols_upper])
        sql = f"""
        SELECT s.ticker, fm.*
        FROM financial_metrics AS fm
        JOIN symbols AS s ON s.id = fm.symbol_id
        WHERE s.ticker IN ({placeholders})
        """
        rows: list[dict] = self.select_query(sql, tuple(symbols_upper))
        rows_clean: list[dict] = [
            {k: v for k, v in row.items() if k != "id" and k != "symbol_id"}
            for row in rows
        ]
    
        return rows_clean

    @ResearchDataCoordinator.register_as_research('news', o=True)
    def get_news(self, symbols: list[str] | str | None = None, limit: int = 10) -> list[dict]:
        """
        Retrieve news articles, optionally filtered by one or more symbols.
        Returns all news ordered by publish date if no symbols provided.

        Args:
            symbols: Single ticker string, list of tickers, or None for all news
            limit: Maximum number of articles to return (default: 10)

        Returns:
            List of dicts containing news article data:
            [
                {
                    'uuid': str,
                    'title': str,
                    'publisher': str,
                    'link': str,
                    'providerPublishTime': int,
                    'thumbnail': str
                },
                ...
            ]
            Returns empty list if no news found.
        """
        if symbols is not None:
            if isinstance(symbols, str):
                symbols = [symbols]
            elif isinstance(symbols, list):
                if not all(isinstance(i, str) for i in symbols):
                    raise ValueError("Symbols paramater must be a string or a list of strings")
            else:
                raise ValueError("Symbols paramater must be a string or a list of strings")

            symbols_upper = [str(s).upper().strip() for s in symbols]
            placeholders = ", ".join(['?' for _ in symbols_upper])

            sql = f"""
            SELECT DISTINCT n.uuid, n.title, n.publisher, n.link,
                   n.providerPublishTime, n.thumbnail
            FROM news n
            JOIN news_symbols ns ON n.id = ns.news_id
            JOIN symbols s ON ns.symbol_id = s.id
            WHERE s.ticker IN ({placeholders})
            ORDER BY n.providerPublishTime DESC
            LIMIT ?
            """
            symbols_upper.append(str(limit))
            return self.select_query(sql, tuple(symbols_upper))

        else:
            sql = """
            SELECT uuid, title, publisher, link,
                   providerPublishTime, thumbnail
            FROM news
            ORDER BY providerPublishTime DESC
            LIMIT ?
            """
            return self.select_query(sql, (limit, ))

    @ResearchDataCoordinator.register_as_research('company_profile', o=True)
    def get_company_profile(self, symbols):
        """
        Retrieve company profile information for one or more symbols.

        Args:
            symbols: Single ticker symbol or list of symbols

        Returns:
            List of dictionaries containing company profile data:
            [
                {
                    'ticker': 'AAPL',
                    'company_desc': 'Apple Inc. designs...',
                    'employee_count': 164000,
                    'industry': 'Consumer Electronics',
                    'sector': 'Industrials',
                    'website': 'https://www.apple.com',
                    'last_updated': '2026-03-05 10:30:00'
                },
                ...
            ]
            Returns empty list if no profiles found

        Example:
            >>> db.get_company_profile('AAPL')
            >>> db.get_company_profile(['AAPL', 'MSFT', 'GOOGL'])
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        if not symbols:
            return []

        symbols = tuple([symbol.upper() for symbol in symbols])
        placeholders = ", ".join(['?' for _ in symbols])

        sql = f"""
        SELECT s.ticker, cp.company_desc, cp.employee_count,
               cp.industry, cp.sector, cp.website, cp.last_updated
        FROM company_profile AS cp
        JOIN symbols AS s ON s.id = cp.symbol_id
        WHERE s.ticker IN ({placeholders})
        """

        return self.select_query(sql, symbols)

    @ResearchDataCoordinator.register_as_research('insider_trades', o=True)
    def get_insider_trades(self, symbols, limit: int = 50):
        """
        Retrieve insider trading transactions for one or more symbols.

        Args:
            symbols: Single ticker symbol or list of symbols
            limit: Maximum number of trades to return per symbol (default: 50)

        Returns:
            List of dictionaries containing insider trade data:
            [
                {
                    'ticker': 'AAPL',
                    'transaction_date': '2024-01-15',
                    'shares': 10000,
                    'transaction_value': 1500000,
                    'filer_name': 'John Doe',
                    'filer_relation': 'Chief Executive Officer',
                    'transaction_text': 'Sale at price...',
                    'last_updated': '2026-03-05 10:30:00'
                },
                ...
            ]
            Returns empty list if no trades found

        Note:
            Results are ordered by transaction_date (newest first)

        Example:
            >>> db.get_insider_trades('AAPL', limit=10)
            >>> db.get_insider_trades(['AAPL', 'MSFT'])
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        if not symbols:
            return []

        symbols = tuple([symbol.upper() for symbol in symbols])
        placeholders = ", ".join(['?' for _ in symbols])

        sql = f"""
        SELECT s.ticker, it.transaction_date, it.shares,
               it.transaction_value, it.filer_name, it.filer_relation,
               it.transaction_text, it.last_updated
        FROM insider_trades AS it
        JOIN symbols AS s ON s.id = it.symbol_id
        WHERE s.ticker IN ({placeholders})
        ORDER BY it.transaction_date DESC
        LIMIT ?
        """

        return self.select_query(sql, symbols + (limit,))

    @ResearchDataCoordinator.register_as_research('stock_splits', o=True)
    def get_stock_splits(self, symbols: list[str] | str) -> list[dict]:
        """
        Retrieve stock split history for one or more symbols.

        Args:
            symbols: Single ticker string or list of tickers

        Returns:
            List of dicts containing stock split data:
            [
                {
                    'ticker': 'AAPL',
                    'split_date': '2020-08-31',
                    'split_ratio': 4.0,
                    'last_updated': '2026-03-05 10:30:00'
                },
                ...
            ]
            Returns empty list if no splits found.

        Note:
            Results ordered by split_date (newest first)
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        if not symbols:
            return []

        symbols_tuple = tuple([symbol.upper() for symbol in symbols])
        placeholders = ", ".join(['?' for _ in symbols])

        sql = f"""
        SELECT s.ticker, ss.split_date, ss.split_ratio, ss.last_updated
        FROM stock_splits AS ss
        JOIN symbols AS s ON s.id = ss.symbol_id
        WHERE s.ticker IN ({placeholders})
        ORDER BY ss.split_date DESC
        """

        return self.select_query(sql, symbols_tuple)
    
    def get_regional_overview(self, symbols) -> List[Dict[str, Union[str, float]]]:
        """
        Retrieve current regional market data from database.
        
        Fetches ETF data for regional market indicators and calculates percent change
        from previous close. Data must be initialized via initialize_regional_etfs()
        before calling this method.
        
        Args:
            symbols: Dict mapping region names to ETF tickers
                    Format: {'USA': 'VOO', 'Europe': 'IEUR', 'Asia': 'VPL', ...}
        
        Returns:
            List of dicts containing regional market data:
            [
                {
                    'region': 'USA',
                    'ticker': 'VOO',
                    'current_price': 614.16,
                    'prev_close': 622.03,
                    'pct_change': -1.27
                },
                {
                    'region': 'Europe',
                    'ticker': 'IEUR',
                    'current_price': 89.45,
                    'prev_close': 90.12,
                    'pct_change': -0.74
                },
                ...
            ]
            Returns empty list if no data found
        
        Note:
            - Percent change calculated as: ((current - prev_close) / prev_close) * 100
            - Requires fresh data from initialize_regional_etfs()
            - Results ordered by region name alphabetically
        
        Example:
            >>> regional_data = db.get_regional_overview(coordinator.SYMBOLS)
            >>> for region in regional_data:
            >>>     print(f"{region['region']}: {region['pct_change']:+.2f}%")
            USA: -1.27%
            Europe: -0.74%
        """
        if not symbols:
            return []
        
        tickers = list(symbols.values())
        placeholders = ", ".join(['?' for _ in tickers])
        
        sql = f"""
            SELECT 
                s.ticker,
                s.last_price as current_price,
                fm.prev_close,
                ((s.last_price - fm.prev_close) / fm.prev_close * 100) as pct_change
            FROM symbols s
            JOIN financial_metrics fm ON s.id = fm.symbol_id
            WHERE s.ticker IN ({placeholders})
        """
        
        rows = self.select_query(sql, tuple(tickers))
        
        if not rows:
            logger.warning("get_regional_overview: no data found")
            return []
        
        # Map ticker symbols back to region names
        ticker_to_region = {v: k for k, v in symbols.items()}
        
        result = []
        for row in rows:
            ticker = row.get('ticker', '')
            if not ticker:
                continue
            
            region = ticker_to_region.get(ticker, ticker)
            
            result.append({
                'region': region,
                'ticker': ticker,
                'current_price': row.get('current_price'),
                'prev_close': row.get('prev_close'),
                'pct_change': round(row.get('pct_change', 0), 2),
            })
        
        # Sort by region name for consistent ordering
        result.sort(key=lambda x: x['region'])
        
        logger.debug(f"Retrieved market data for {len(result)} regions")
        return result
    
    def get_screener_results(self, screener_names: list[str] | str | None=None, limit: int = 10) -> List[Dict[str, Union[int, str, float]]]:
        """
        Retrieve top N stocks from a screener with current market data.

        Fetches ranked stocks from a screener along with real-time pricing, volume,
        and market cap data. Designed for homepage screener widgets.

        Args:
            screener_name: Name of screener to query
                          Options: 'day_gainers', 'day_losers', 'most_actives',
                                  'most_watched_tickers', 'fifty_two_wk_gainers',
                                  'fifty_two_wk_losers', 'volume_spike_bullish',
                                  'volume_spike_bearish'
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of dicts containing screener results with current data:
            [
                {
                    'screener_name': 'day_gainers',
                    'rank': 1,
                    'ticker': 'NVDA',
                    'company_name': 'NVIDIA Corporation',
                    'current_price': 875.43,
                    'prev_close': 862.10,
                    'price_change_pct': 1.55,
                    'market_cap': 2150000000000,
                    'todays_volume': 45000000,
                    'three_month_avg_volume': 38000000,
                    'volume_change_pct': 18.42
                },
                ...
            ]
            Returns empty list if screener not found or no results

        Note:
            - Requires fresh data from set_screeners_metadata() and set_financial_metrics()
        """
        from MarketOverviewCoordinator import YQ_SCREENER_NAMES, CUSTOM_SCREENERS
        valid_screeners = YQ_SCREENER_NAMES + CUSTOM_SCREENERS
        if screener_names is None:
            screener_names = valid_screeners

        safe_screener_names: list[str] = []
        if isinstance(screener_names, list):
            try:
                for n in screener_names:
                    safe_screener_names.append(str(n))
            except Exception as e:
                logger.exception(e)
                ValueError("'screener_names' must be a str or list of strs.")
        elif not isinstance(screener_names, str):
            try:
                safe_screener_names.append(str(n))
            except Exception as e:
                logger.exception(e)
                ValueError("'screener_names' must be a str or list of strs.")
        else:
            safe_screener_names.append(screener_names)
        
        invalid_screeners = []
        for idx, screener in enumerate(safe_screener_names):
            if screener not in valid_screeners:
                invalid_screeners.append(screener)
                safe_screener_names.pop(idx)
        if invalid_screeners:
            logger.warning(f"Screener parameters {invalid_screeners} are invalid...skipping")

        placeholders = ", ".join("?" for _ in safe_screener_names)
        safe_screener_names.append(str(limit)) 
        sql = f"""
            SELECT 
                sr.screener_name AS screener_name,
                sr.rank AS rank,
                s.ticker AS ticker,
                s.company_name AS company_name,
                s.last_price AS current_price,
                fm.prev_close AS prev_close,
                (((s.last_price - fm.prev_close) / fm.prev_close) * 100.00) AS price_change_pct,
                fm.market_cap AS market_cap,
                fm.todays_volume AS todays_volume,
                fm.three_month_avg_volume AS three_month_avg_volume,
                (((CAST(fm.todays_volume AS REAL) - fm.three_month_avg_volume) / fm.three_month_avg_volume) * 100.00) AS volume_change_pct
            FROM screener_results AS sr
            JOIN symbols AS s ON sr.symbol_id = s.id
            JOIN financial_metrics AS fm ON s.id = fm.symbol_id
            WHERE sr.screener_name in ({placeholders})
            ORDER BY sr.rank
            LIMIT ?
        """
        rows = self.select_query(sql, tuple(safe_screener_names))
    
        if not rows:
            logger.warning(f"get_screener_results: no results found for screeners '{screener_names}'")
            return []

        rankings = []
        for row in rows:
            data = {
                'screener_name': row['screener_name'],
                'rank': row['rank'],
                'ticker': row['ticker'],
                'company_name': row['company_name'],
                'current_price': row['current_price'],
                'prev_close': row['prev_close'],
                'price_change_pct': round(row['price_change_pct'], 2) if row['price_change_pct'] is not None else 0.0,
                'market_cap': row['market_cap'],
                'todays_volume': row['todays_volume'],
                'three_month_avg_volume': row['three_month_avg_volume'],
                'volume_change_pct': round(row['volume_change_pct'], 2) if row['volume_change_pct'] is not None else 0.0
            }
            rankings.append(data)

        return rankings