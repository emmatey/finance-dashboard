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

    def upsert_symbol(self, symbol: str, price_module_raw: dict):
        """
        Upsert symbol record in database.

        Args:
            symbol: Stock symbol (e.g. 'AAPL')
            price_module: Result of Ticker.price call.
        """
        symbol = symbol.upper()
        price_module = price_module_raw[symbol].get('price')
        company_name = (
            price_module.get('longName') or 
            price_module.get('shortName') or 
            symbol.upper()
        )
        last_price = price_module.get('regularMarketPrice', 0)

        sql = """
        INSERT INTO symbols (ticker, company_name, last_price, last_updated)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(ticker) DO UPDATE SET
            company_name = excluded.company_name,
            last_price = excluded.last_price,
            last_updated = CURRENT_TIMESTAMP
        """
        self.simple_query(sql, (symbol, company_name, last_price))

        logger.info(f"{symbol} written to DB!")

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
        metrics: Dict[str, Dict[str, Optional[Union[float, str, int]]]]
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

        sql = f"""
            INSERT INTO financial_metrics (symbol_id, {table_cols_str})
            SELECT id, {placeholders}
            FROM symbols
            WHERE ticker = ?
            ON CONFLICT(symbol_id)
            DO UPDATE SET
            last_updated=CURRENT_TIMESTAMP, {excluded_cols_str}
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
            news_data: List of news article dictionaries from yq_search_get_news()
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
        ticker_set = {ticker for v in related_uuids.values() for ticker in v}
        ticker_placeholders = ", ".join(["?" for _ in ticker_set])

        # Find news id for associated uuid
        uuid_sql = f"""
        SELECT uuid, id AS news_id
        FROM news
        WHERE uuid IN ({uuid_placeholders})
        """
        uuid_rows = self.simple_query(uuid_sql, tuple(uuid_set))
        uuid_cipher = {i.get('uuid'): i.get('news_id') for i in uuid_rows} # type: ignore

        # Find symbol id for associated ticker
        ticker_sql = f"""
        SELECT ticker, id as symbol_id
        FROM symbols
        WHERE ticker in ({ticker_placeholders})
        """
        ticker_rows = self.simple_query(ticker_sql, tuple(ticker_set))
        ticker_cipher = {i.get('ticker'): i.get('symbol_id') for i in ticker_rows} # type: ignore

        # go from {uuid: [ticker]} to {news_id: [ticker_id]}
        translated_related_uuids = {}
        for uuid, tickers in related_uuids.items():
            buffer = []
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
                                     'website': 'https://www.apple.com'
                                 },
                                 'MSFT': {
                                     'company_desc': 'Microsoft Corporation develops...',
                                     'employee_count': 221000,
                                     'industry': 'Software—Infrastructure',
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
            logger.warning(
                "set_insider_trades aborted: empty trade_data dict")
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

    def set_screeners(self, screener_metadata: Dict[str, List[str]], yqs_instance) -> None:
        """
        Update screener results in the database with fresh data.

        Clears all existing screener data and replaces it with current rankings.
        Ensures all tickers exist in the symbols table before insertion, fetching
        missing ticker data from Yahoo Finance as needed.

        Args:
            screener_metadata: Output from extract_screener_data_for_db()
                              Format: {
                                  'day_gainers': ['NVDA', 'TSLA', 'AMD', ...],
                                  'most_actives': ['AAPL', 'MSFT', 'GOOGL', ...],
                                  'volume_spikes': ['ULTA', 'KYIV', ...]
                              }
                              Each list is ordered by rank (index 0 = rank 1)
            yqs_instance: YahooQueryService instance for fetching missing ticker data

        Returns:
            None

        Database Operations:
            1. Validates all tickers exist in symbols table (fetches if missing)
            2. Deletes all existing screener_results rows
            3. Inserts fresh screener data with current rankings

        Note:
            - This is a full table replacement, not an upsert
            - Silently skips tickers that cannot be fetched from Yahoo Finance
            - Auto-incremented IDs continue incrementing (not reset to 1)
            - Rank values start at 1 for each screener
            - last_updated timestamp is auto-set by database

        Example:
                 # Full pipeline
            >>> raw = yqs.yq_screener_get_screeners(['day_gainers', 'most_actives'], count=25)
            >>> filtered = yqs._filter_screener_data(raw)
            >>> volume_swings = yqs.get_relative_volumes(filtered)
            >>> filtered.update(volume_swings)
            >>> screener_data = yqs.extract_screener_data_for_db(filtered)
            >>> db_io.set_screeners(screener_data, yqs)
            INFO: Inserted 50 fresh screener results across 2 screeners
        """

        # Collect all unique tickers across all screeners
        all_tickers: set[str] = set()
        for tickers in screener_metadata.values():
            all_tickers.update(tickers)

        # Query database for existing tickers
        if not all_tickers:
            logger.warning("No tickers to process")
            return

        placeholders = ','.join('?' * len(all_tickers))
        existing_tickers_query = self.simple_query(
            f"SELECT ticker FROM symbols WHERE ticker IN ({placeholders})",
            tuple(all_tickers)
        )

        # Create set of existing tickers
        existing_tickers: set[str] = {row['ticker'] for row in existing_tickers_query}

        # Find tickers that need to be fetched
        missing_tickers = all_tickers - existing_tickers

        # Fetch and insert missing tickers
        if missing_tickers:
            logger.info(f"Fetching data for {len(missing_tickers)} new tickers: {missing_tickers}")
            modules = yqs_instance.yq_ticker_get_modules(list(missing_tickers), ['price'])

            for ticker in missing_tickers:
                # Fetch price module from Yahoo Finance
                if modules and ticker in modules:
                    self.upsert_symbol(ticker, modules)
                else:
                    logger.warning(f"Could not fetch data for {ticker}, skipping")
        else:
            logger.debug("All tickers already exist in symbols table")
        
        # Clear old screener data.
        self.simple_query("DELETE FROM screener_results")

        # Insert/update screener results
        sql = sql = """
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
        logger.info(f"Upserted {len(screener_tuples)} screener results across {len(screener_metadata)} screeners")


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

        return self.simple_query(sql, symbols)

    @ResearchDataCoordinator.register_as_research('financial_metrics', o=True)
    def get_financial_metrics(self, symbols):
        """
        list of dicts
        returns

        """
        if isinstance(symbols, str):
            symbols = [symbols]
        if not symbols:
            return []

        symbols = tuple([symbol.upper() for symbol in symbols])
        placeholders = ", ".join(['?' for _ in symbols])

        sql = f"""
        SELECT s.ticker, fm.*
        FROM financial_metrics AS fm
        JOIN symbols AS s ON s.id = fm.symbol_id
        WHERE s.ticker IN ({placeholders})
        """

        rows = self.simple_query(sql, symbols)
        rows_clean = []
        for row in rows: # type: ignore
            # remove primary key from select *
            rows_clean.append({k: v for k, v in row.items() if k != "id" and k != "symbol_id"})

        return rows_clean

    @ResearchDataCoordinator.register_as_research('news', o=True)
    def get_news(self, symbol = None, limit = 10):
        """
        Retrieve news articles, optionally filtered by symbol.

        Returns list of dicts with article info.
        """

        if symbol:
            sql = """
            SELECT n.uuid, n.title, n.publisher, n.link,
                   n.providerPublishTime, n.thumbnail
            FROM news n
            JOIN news_symbols ns ON n.id = ns.news_id
            JOIN symbols s ON ns.symbol_id = s.id
            WHERE s.ticker = ?
            ORDER BY n.providerPublishTime DESC
            LIMIT ?
            """
            return self.simple_query(sql, (symbol.upper(), limit))
        else:
            sql = """
            SELECT uuid, title, publisher, link,
                   providerPublishTime, thumbnail
            FROM news
            ORDER BY providerPublishTime DESC
            LIMIT ?
            """
            return self.simple_query(sql, (limit,))

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
               cp.industry, cp.website, cp.last_updated
        FROM company_profile AS cp
        JOIN symbols AS s ON s.id = cp.symbol_id
        WHERE s.ticker IN ({placeholders})
        """

        return self.simple_query(sql, symbols)

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
        JOIN symbols AS s ON s.id = it.symbol_idk
        WHERE s.ticker IN ({placeholders})
        ORDER BY it.transaction_date DESC
        LIMIT ?
        """

        return self.simple_query(sql, symbols + (limit,))

    def get_regional_overview(self, symbols) -> Dict[str, Dict[str, float]]:
        """
        Retrieve current regional market data from database.
        
        Args: Symbols, the dict mapping region to etf which represents said region's market.
            eg. symbols = {
            'USA' = 'VOO',
            'EU' = 'IEUR',
            ...
            }

        Returns:
            Dict mapping region names to market data:
            {
                'USA': {
                    'ticker': 'VOO',
                    'current_price': 614.16,
                    'prev_close': 622.03,
                    'pct_change': -1.27
                },
                ...
            }
        """
        symbols = list(symbols.values())
        placeholders = ", ".join(['?' for _ in symbols])
        
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
        
        rows = self.simple_query(sql, tuple(symbols))
        assert isinstance(rows, list)
        
        # Map ticker symbols back to region names
        ticker_to_region = {v: k for k, v in symbols.items()}
        
        result = {}
        for row in rows:
            ticker = row.get('ticker', '')
            if not ticker:
                continue
                
            region = ticker_to_region.get(ticker, ticker)
            
            result[region] = {
                'ticker': ticker,
                'current_price': row.get('current_price'),
                'prev_close': row.get('prev_close'),
                'pct_change': round(row.get('pct_change', 0), 2),
            }
        
        logger.debug(f"Retrieved market data for {len(result)} regions")
        return result