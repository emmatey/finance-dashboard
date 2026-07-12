import datetime
import logging
import pandas as pd
import yahooquery as yq
from collections import defaultdict
from DbManager import DbManager
from helpers import TickerNotFoundError
from ResearchDataCoordinator import ResearchDataCoordinator
from typing import List, Tuple, Dict, Union, Any, Optional
from YahooAPIClient import yq_exception_handler

logger = logging.getLogger(__name__)


class YahooQueryService:
    """
    Service layer for Yahoo Finance API interactions to support the /research route.

    Provides methods to fetch stock data, news, and financial metrics
    using yahooquery library.
    """

    @yq_exception_handler()
    def yq_search(self, query: str, quotes_count: int = 20, news_count: int = 0) -> dict | None:
        """
        Search for symbols by company name or ticker using Yahoo Finance search.
        
        Wrapped with circuit breaker exception handling.
        
        Args:
            query: Company name or ticker fragment to search for
            quotes_count: Maximum number of quote results to return (default: 20)
            news_count: Maximum number of news results to return (default: 0)
            
        Returns:
            Dict with keys 'quotes' (list of symbol results) and optionally 'news'
            None if API is down or request fails
            
        https://yahooquery.dpguthrie.com/guide/misc/#search
        """
        res = yq.search(query, news_count=news_count, quotes_count=quotes_count)
        return res
    
    @DbManager.time_method
    @yq_exception_handler()
    def yq_ticker_fetch_modules(
        self,
        symbols: Union[List[str], str],
        modules: Union[List[str], str]
    ) -> Dict[str, Any]:
        """
        Fetch specific data modules for one or more stock symbols.

        Wraps yahooquery's get_modules method to retrieve structured data
        like price, statistics, financial data, etc.

        Args:
            symbols: Single stock ticker symbol or list of symbols (e.g., 'AAPL' or ['AAPL', 'MSFT'])
            modules: Single module name or list of module names to fetch
                    (e.g., 'price', ['price', 'summaryDetail'])

        Returns:
            Dictionary containing requested module data in format:
            {symbol: {module_name: {data...}}}
            Returns empty dict on error

        Raises:
            ValueError: If symbols is not a string or list, or module is invalid.
            TickerNotFoundError: If ticker not found on yahooquery.

        Reference:
            https://yahooquery.dpguthrie.com/guide/ticker/modules/#get_modules
        """
        # Type safety for symbols - normalize to list
        if isinstance(symbols, str):
            symbols = [symbols.upper()]
        elif isinstance(symbols, list):
            symbols = [str(i).upper() for i in symbols]
        else:
            logger.warning(f"{symbols} is an invalid input")
            raise ValueError("Symbols argument must be a stock ticker string or list of tickers.")

        # Type safety for modules - normalize to list
        safe_modules: List[str] = []
        if isinstance(modules, str):
            safe_modules.append(modules)
        elif isinstance(modules, list):
            safe_modules = [str(i) for i in modules]

        ticker = yq.Ticker(symbols)
        raw_modules = ticker.get_modules(safe_modules)

        if not isinstance(raw_modules, dict):
            logger.warning(f"Yahoo API Error for {symbols}: {raw_modules}")
            return {}

        # Normalize single-module response structure.
        if len(safe_modules) == 1:
            module_name = safe_modules[0]
            return {symbol: {module_name: data} for symbol, data in raw_modules.items()}
        
        for ticker in raw_modules:
            if isinstance(raw_modules[ticker], str):
                if "Quote not found for symbol" in raw_modules[ticker]:
                    raise TickerNotFoundError(f"Ticker {ticker} not found.")

        return raw_modules

    @ResearchDataCoordinator.register_as_research('historical_prices', api=True)
    @yq_exception_handler()
    def yq_ticker_fetch_historical_prices(
        self,
        symbol: str,
        period: str = "5y",
        interval: str = "1d"
    ) -> Optional[List[Tuple[str, float, int, str]]]:
        """
        Fetch historical price and volume data for a stock.

        Returns timezone-aware (UTC) historical data including adjusted close
        prices and trading volumes.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            period: Length of time to retrieve
                   Options: ['1d', '5d', '7d', '60d', '1mo', '3mo', '6mo',
                            '1y', '2y', '5y', '10y', 'ytd', 'max']
            interval: Time between data points
                     Options: ['1m', '2m', '5m', '15m', '30m', '60m', '90m',
                              '1h', '1d', '5d', '1wk', '1mo', '3mo']

        Returns:
            A list of tuples (date, close, volume, symbol) where:
                - date: 'YYYY-MM-DD' string (sqlite3 can't bind a pandas Timestamp)
                - close: Adjusted close price (float)
                - volume: Trading volume (int)
                - symbol: Stock ticker
            Returns None if data retrieval fails or the DataFrame is empty.

        Reference:
            https://yahooquery.dpguthrie.com/guide/ticker/historical/
        """
        symbol = symbol.upper()
        ticker = yq.Ticker(symbol)
        df = ticker.history(period=period, interval=interval, adj_ohlc=True, adj_timezone=False)

        if isinstance(df, pd.DataFrame) and not df.empty:
            # Flatten multidex
            df_flat = df.reset_index()

            # Select required data
            df_subset = df_flat[['date', 'close', 'volume', 'symbol']].copy()

            # Filter out any rows where ANY of the three target columns are empty
            df_filter = df_subset.dropna(subset=['date', 'close', 'volume', 'symbol'])

            # sqlite3 can't bind a pandas Timestamp, and Yahoo inconsistently returns
            # either plain datetime.date (most tickers) or tz-aware Timestamps (e.g.
            # thinly-traded/warrant symbols) for the 'date' column depending on the
            # ticker. pd.to_datetime() normalizes both cases before formatting to the
            # same YYYY-MM-DD string the rest of the codebase uses for DATETIME columns.
            df_filter = df_filter.copy()
            df_filter['date'] = pd.to_datetime(df_filter['date']).dt.strftime('%Y-%m-%d')

            # Convert to list of tuples
            data_tuples = df_filter.values.tolist()

            return [tuple(i) for i in data_tuples]

        else:
            logger.warning(f"Price retrieval error for {symbol}.")
            return None

    @ResearchDataCoordinator.register_as_research('stock_splits', api=True)
    @yq_exception_handler()
    def yq_ticker_fetch_stock_splits(
        self,
        symbols: Union[List[str], str],
        period: str = "5y"
    ) -> List[Tuple[str, float, str]]:
        """
        Retrieve historical stock split data for one or more symbols.

        Args:
            symbols: Single ticker symbol or list of symbols
            period: Time period to search for splits
                   Options: ['1d', '5d', '7d', '60d', '1mo', '3mo', '6mo',
                            '1y', '2y', '5y', '10y', 'ytd', 'max']

        Returns:
            List of tuples containing (date, split_ratio, symbol), where date is a
            'YYYY-MM-DD' string (sqlite3 can't bind a pandas Timestamp)
            Returns empty list if no splits found or on error

        Example:
            >>> service.yq_ticker_stock_splits(['AAPL'])
            [('2020-08-31', 4.0, 'AAPL'), ...]
        """
        if isinstance(symbols, str):
            symbols = [symbols.upper()]
        else:
            symbols = [i.upper() for i in symbols]

        t = yq.Ticker(symbols)
        df = t.history(period=period)

        if df.empty or 'splits' not in df.columns:
            logger.warning(f"No stock split data received for {symbols}")
            return []

        # Filter for only rows where splits occurred (value > 0)
        # Reference: https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html#boolean-indexing
        try:
            splits = df['splits'][df['splits'] > 0].reset_index()
        except KeyError:
            return []

        # sqlite3 can't bind a pandas Timestamp - store as the same YYYY-MM-DD
        # string format the rest of the codebase uses for DATETIME columns.
        dates: List[str] = pd.to_datetime(splits['date']).dt.strftime('%Y-%m-%d').tolist()
        split_ratios: List[float] = splits['splits'].tolist()
        symbols_list: List[str] = splits['symbol'].tolist()

        return list(zip(dates, split_ratios, symbols_list))

    @ResearchDataCoordinator.register_as_research('news', api=True)
    @yq_exception_handler()
    def yq_search_fetch_news(self, symbol: str, qty: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch and process news articles for a stock symbol.
        Wraps yq.search() with circuit breaker, returns processed news ready for set_news().
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            qty: Maximum number of articles to return (default: 10)
    
        Returns:
            List of processed news dicts ready for set_news().
            Returns empty list if no news found.
        """
        if not isinstance(symbol, str):
            raise ValueError("'symbol' must be a string ticker e.g. 'AAPL'")
        
        raw = yq.search(symbol.upper())
        if not raw:
            return []
        
        return self.extract_news(raw, qty=qty)
    
    def extract_news(self, response: dict, qty: int = 10) -> List[Dict[str, Any]]:
        """
        Extract and normalize news articles from a raw yq.search() response.
        Can be called directly with a raw search response to avoid a second API call.
    
        Args:
            response: Raw dict from yq.search() or yq_search_fetch_news()
            qty: Maximum number of articles to return (default: 10)
    
        Returns:
            List of dicts with keys: uuid, title, publisher, link,
            providerPublishTime, thumbnail, relatedTickers.
            Returns empty list if no news found.
        """
        data: List[Dict[str, Any]] = response.get('news', [])
        if not data:
            return []
    
        # Sort newest first, truncate to qty
        news = sorted(data, key=lambda item: item.get('providerPublishTime', 0), reverse=True)[:qty]
    
        desired_keys = ['uuid', 'title', 'publisher', 'link', 'providerPublishTime', 'thumbnail', 'relatedTickers']
    
        for story in news:
            # Filter to desired keys
            for key in list(story.keys()):
                if key not in desired_keys:
                    del story[key]
    
            # Extract thumbnail URL from nested structure; prefer index 1 (medium res) when available
            thumbnail_url = "N/A"
            resolutions = story.get("thumbnail", {})
            if isinstance(resolutions, dict):
                images = resolutions.get("resolutions", [])
                if images:
                    try:
                        idx = 1 if len(images) > 1 else 0
                        thumbnail_url = images[idx].get("url", "N/A")
                    except (IndexError, AttributeError):
                        pass
            story["thumbnail"] = thumbnail_url
    
        return news

    @ResearchDataCoordinator.register_as_research('financial_metrics', api=True, modules=['price', 'defaultKeyStatistics', 'summaryDetail', 'financialData'])
    def extract_financial_metrics(
        self,
        modules_dict: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Optional[Union[float, str]]]]:
        """
        Extract and format key financial metrics from Yahoo Query module data.

        Consolidates data from multiple API modules into a single dictionary
        of commonly used valuation and performance metrics for multiple companies.

        Args:
            modules_dict: Raw modules dictionary from yq_ticker_get_modules()
                         Format: {symbol: {module_name: {data...}}}
                         Required modules: 'price', 'defaultKeyStatistics',
                                         'summaryDetail', 'financialData'

        Returns:
            Dictionary containing formatted metrics for each symbol:
            {symbol: {
                Core Pricing: market_open, prev_close, market_cap
                Valuation: beta, eps, trailing_pe, forward_pe, profit_margin
                Range/Yield: dividend_yield, fifty_two_week_high/low
                Analyst Data: rating, target_price, analyst_count
                Health: current_ratio, debt_to_equity
            }}

            All values are Optional (may be None if not available)

        Example:
            >>> modules = service.yq_ticker_get_modules(['AAPL', 'MSFT'],
                    ['price', 'defaultKeyStatistics', 'summaryDetail', 'financialData'])
            >>> metrics = service.get_financial_metrics(modules)
            >>> metrics['AAPL']['market_cap']
            2500000000000

        Reference:
            https://yahooquery.dpguthrie.com/guide/ticker/modules
        """
        if not modules_dict:
            return {}

        out = {}

        for symbol, data in modules_dict.items():
            price = data.get('price', {})
            defaultKeyStatistics = data.get('defaultKeyStatistics', {})
            summaryDetail = data.get('summaryDetail', {})
            financialData = data.get('financialData', {})

            # THIS MUST MATCH DB SCHEMA
            metrics: Dict[str, Optional[Union[float, str]]] = {
                # Core Pricing Context (price module)
                "market_open": price.get('regularMarketOpen'),
                "prev_close": price.get('regularMarketPreviousClose'),
                "market_cap": price.get('marketCap'),
                "todays_change": price.get("regularMarketChange"),
                "todays_change_pct": price.get("regularMarketChangePercent"),

                # Valuation & Risk (defaultKeyStatistics module)
                "beta": defaultKeyStatistics.get('beta'),
                "eps": defaultKeyStatistics.get('trailingEps'),
                "trailing_pe": defaultKeyStatistics.get('trailingPE'),
                "forward_pe": defaultKeyStatistics.get('forwardPE'),
                "profit_margin": defaultKeyStatistics.get('profitMargins'),
                "shares_outstanding": defaultKeyStatistics.get('sharesOutstanding'),
                "book_value": defaultKeyStatistics.get('bookValue'),
                "price_to_book": defaultKeyStatistics.get('priceToBook'),

                # Range & Yield (summaryDetail module)
                "dividend_yield": summaryDetail.get('dividendYield'),
                "fifty_two_week_high": summaryDetail.get('fiftyTwoWeekHigh'),
                "fifty_two_week_low": summaryDetail.get('fiftyTwoWeekLow'),
                "fifty_day_average": summaryDetail.get('fiftyDayAverage'),
                "two_hundred_day_average": summaryDetail.get('twoHundredDayAverage'),

                # Analyst Sentiment & Health (financialData module)
                "rating": financialData.get('recommendationKey'),
                "target_price": financialData.get('targetMeanPrice'),
                "analyst_count": financialData.get('numberOfAnalystOpinions'),
                "current_ratio": financialData.get('currentRatio'),
                "debt_to_equity": financialData.get('debtToEquity'),

                # Volume Over Time
                "todays_volume": summaryDetail.get('regularMarketVolume'),
                "ten_day_avg_volume": summaryDetail.get('averageVolume10days'),
                "three_month_avg_volume": summaryDetail.get('averageVolume')
            }
            out[symbol] = metrics

        return out

    @ResearchDataCoordinator.register_as_research('company_profile', api=True, modules=['summaryProfile'])
    def extract_company_overview(
        self,
        modules_dict: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Extract company overview information from summary profile data.

        Args:
            modules_dict: Raw modules dictionary from yq_ticker_get_modules()
                         Format: {symbol: {module_name: {data...}}}
                         Required module: 'summaryProfile'

        Returns:
            Dictionary containing company info for each symbol:
            {symbol: {
                company_desc: Long-form business description
                employee_count: Number of full-time employees (int or "N/A")
                industry: Industry classification
                sector: Sector classification
                website: Company website URL
            }}

        Example:
            >>> modules = service.yq_ticker_get_modules(['AAPL'], ['summaryProfile'])
            >>> overview = service.get_company_overview(modules)
            >>> overview['AAPL']['industry']
            'Consumer Electronics'

        Note:
            All fields return default values if not found in source data.
        """
        if not modules_dict:
            return {}

        out = {}

        for symbol, data in modules_dict.items():
            summaryProfile = data.get("summaryProfile")
            if not summaryProfile:
                logger.warning(f"Unable to get summaryProfile module for {symbol}")
                continue

            company_data: Dict[str, Union[str, int]] = {
                "company_desc": summaryProfile.get("longBusinessSummary", "No description available."),
                "employee_count": summaryProfile.get("fullTimeEmployees", "Unknown"),
                "industry": summaryProfile.get("industry", "Unknown"),
                "sector": summaryProfile.get("sector", "Unknown"),
                "website": summaryProfile.get("website", "Unknown")
            }

            out[symbol] = company_data

        return out

    @ResearchDataCoordinator.register_as_research('insider_trades', api=True, modules=['insiderTransactions'])
    def extract_insider_trades(
        self,
        module_dict,
        timeframe_in_years: int = 5
    ):
        """
        Extract and filter insider trading transaction data.

        Filters transactions to only include those within the specified timeframe
        and removes extraneous fields from the API response.

            Args:
                module_dict: Raw modules dictionary from yq_ticker_get_modules()
                             Format: {symbol: {module_name: {data...}}}
                             Required module: 'insiderTransactions'
                             Structure: {
                                 'AAPL': {
                                     'insiderTransactions': {
                                         'transactions': [
                                             {
                                                 'startDate': '2024-01-15',
                                                 'shares': 10000,
                                                 ...
                                             }
                                         ]
                                     }
                                 }
                             }
            timeframe_in_years: Number of years of history to include (default: 5)
                               Transactions older than this are filtered out

        Returns:
            Dictionary containing filtered insider trades for each symbol:
            {symbol: [
                {
                    startDate: Transaction date (string: 'YYYY-MM-DD')
                    shares: Number of shares traded
                    value: Transaction value
                    filerName: Name of insider
                    filerRelation: Insider's relationship to company
                    transactionText: Description of transaction type
                },
                ...
            ]}
            Returns empty list for symbols with no transactions available
        """
        if not module_dict:
            return {}

        N_YRS = datetime.timedelta(days=(365 * timeframe_in_years))
        today = datetime.datetime.today()
        n_yrs_ago = today - N_YRS

        field_map = {
            "startDate": "transaction_date",
            "shares": "shares",
            "value": "transaction_value",
            "transactionText": "transaction_text",
            "filerName": "filer_name",
            "filerRelation": "filer_relation"
        }

        out = {}

        for symbol, data in module_dict.items():
            insiderTransactions = data.get("insiderTransactions", {})
            transactions_list = insiderTransactions.get('transactions')
            if not transactions_list:
                out[symbol] = []
                continue

            filtered_transactions = []
            for tx in transactions_list:
                try:
                    tx_date = datetime.datetime.strptime(tx.get('startDate', "1970-01-01"), "%Y-%m-%d")
                except (ValueError, TypeError):
                    continue

                # Skip transaction if older than 5 yrs
                if tx_date < n_yrs_ago:
                    continue

                # Filter for required keys
                tmp_tx = {}
                for raw, updated in field_map.items():
                    tmp_tx[updated] = tx.get(raw)

                # Handle NULL values in "transaction_value" field.
                transaction_value = tmp_tx.get('transaction_value')
                transaction_text = tmp_tx.get('transaction_text')
                placeholder_str = "Option Exercise / Award / Director Compensation"

                # If transaction text isn't falsy, leave it in place.
                if transaction_value is None and not transaction_text:
                    tmp_tx['transaction_text'] = placeholder_str

                filtered_transactions.append(tmp_tx)

            out[symbol] = filtered_transactions

        return out

    @DbManager.time_method
    @yq_exception_handler()
    def yq_screener_fetch_screeners(self, screeners: List[str] | str, count: int = 25) -> Dict:
        """
        In the style of get_modules, query yahoo API for screener objects.

        Args: screeners: a list of the names of the screeners requested.

        Screener Format: https://yahooquery.dpguthrie.com/guide/screener/#get_screeners
        """
        # Call get_screeners
        s = yq.Screener()
        screener_results = s.get_screeners(screeners, count)

        return screener_results

    def _filter_screener_data(
        self, 
        screeners: Dict[str, Dict[str, List[Dict[str, Any]]]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filter screener results to remove low-quality securities.
        
        Filtering criteria:
            1. Share price > $1.00
            2. Market cap ≥ $50,000,000
            3. Exclude Pink Sheets/OTC exchanges ['PNK', 'OTC']
            4. Average 10-day volume > 200,000
        
        Args:
            screeners: Raw screener data from yahooquery
                      Format: {
                          'screener_name': {
                              'quotes': [
                                  {company_data},
                                  {company_data}
                              ]
                          }
                      }
        
        Returns:
            Filtered screener data: {screener_name: [filtered_quotes]}
        
        Reference:
            https://yahooquery.dpguthrie.com/guide/screener/#get_screeners
        """
        filtered_screeners: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Track filtering stats
        total_processed = 0
        processed_successfully = 0
        filter_reasons = defaultdict(int)  # Track why stocks were filtered
        
        for screener_name, data in screeners.items():
            logger.debug(f"Processing screener: {screener_name}")
            
            quotes: List[Dict] = data.get('quotes', [])
            
            if not quotes:
                logger.warning(f"No quote data available for '{screener_name}'")
                continue
            
            initial_count = len(quotes)
            logger.debug(f"  Initial quotes: {initial_count}")
            
            for quote in quotes:
                total_processed += 1
                
                # Extract filter criteria
                share_price = quote.get('regularMarketPrice', 0)
                market_cap = quote.get('marketCap', 0)
                exchange = quote.get('exchange', '').upper()
                avg_volume_10d = quote.get('averageDailyVolume10Day', 0)
                symbol = quote.get('symbol', 'UNKNOWN')
                
                # Apply filters with logging
                if share_price < 1.00:
                    filter_reasons['price_too_low'] += 1
                    logger.debug(f"  Removed {symbol}: Price ${share_price:.2f} < $1.00")
                    continue
                
                if market_cap < 50_000_000:
                    filter_reasons['market_cap_too_low'] += 1
                    logger.debug(f"  Removed {symbol}: Market cap ${market_cap:,.0f} < $50M")
                    continue
                
                if exchange in ['PNK', 'OTC']:
                    filter_reasons['excluded_exchange'] += 1
                    logger.debug(f"  Removed {symbol}: Exchange '{exchange}' is Pink Sheets/OTC")
                    continue
                
                if avg_volume_10d < 200_000:
                    filter_reasons['volume_too_low'] += 1
                    logger.debug(f"  Removed {symbol}: Avg volume {avg_volume_10d:,.0f} < 200,000")
                    continue
                
                # Passed all filters
                filtered_screeners[screener_name].append(quote)
                processed_successfully += 1
            
            final_count = len(filtered_screeners[screener_name])
            filtered_out = initial_count - final_count
            
            logger.info(
                f"Screener '{screener_name}': {final_count}/{initial_count} passed filters "
                f"({filtered_out} filtered out)"
            )
        
        # Summary logging
        logger.info(
            f"Filtering complete: {processed_successfully}/{total_processed} quotes passed filters "
            f"({total_processed - processed_successfully} filtered out)"
        )
        
        if filter_reasons:
            logger.info("Filter breakdown:")
            for reason, count in sorted(filter_reasons.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  - {reason}: {count}")
        
        return dict(filtered_screeners)
 
    def extract_screener_metadata(self, screeners: Dict) -> Dict[str, List[str]]:
        """
        Extract screener data required for database insertion.
        """
        extracted = {}

        for screener, quotes in screeners.items():
            tickers = []
            for quote in quotes:
                # Screeners are already ordered.
                tickers.append(quote.get('symbol'))
            
            extracted[screener] = tickers

        return extracted
    
    def extract_screener_data(self, screeners: Dict) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
        """
        Extract data from screener quotes for database insertion.
        
        Merges data from duplicate tickers across screeners, preferring non-None values.
        """
        financial_metrics_aggregate = {}
        price_modules_aggregate = {}
        
        for screener_name, quotes in screeners.items():
            logger.debug(f"Extracting data from {screener_name}")
            
            for quote in quotes:
                ticker = quote.get('symbol')
                
                # Extract price module data
                price_data = {
                    'symbol': ticker,
                    'quoteType': quote.get('quoteType'),
                    'longName': quote.get('longName'),
                    'shortName': quote.get('shortName'),
                    'regularMarketPrice': quote.get('regularMarketPrice'),
                    'exchange': quote.get('exchange')
                }
                
                # Extract financial metrics
                metrics_data = {
                    'market_open': quote.get('regularMarketOpen'),
                    'prev_close': quote.get('regularMarketPreviousClose'),
                    'market_cap': quote.get('marketCap'),
                    'eps': quote.get('epsTrailingTwelveMonths'),
                    'beta': quote.get('beta'),
                    'trailing_pe': quote.get('trailingPE'),
                    'forward_pe': quote.get('forwardPE'),
                    'profit_margin': quote.get('profitMargins'),
                    'shares_outstanding': quote.get('sharesOutstanding'),
                    'book_value': quote.get('bookValue'),
                    'price_to_book': quote.get('priceToBook'),
                    'dividend_yield': quote.get('trailingAnnualDividendYield'),
                    'fifty_two_week_high': quote.get('fiftyTwoWeekHigh'),
                    'fifty_two_week_low': quote.get('fiftyTwoWeekLow'),
                    'fifty_day_average': quote.get('fiftyDayAverage'),
                    'two_hundred_day_average': quote.get('twoHundredDayAverage'),
                    'rating': quote.get('averageAnalystRating'),
                    'analyst_count': None,
                    'target_price': None,
                    'current_ratio': None,
                    'debt_to_equity': None,
                    'todays_volume': quote.get('regularMarketVolume'),
                    'ten_day_avg_volume': quote.get('averageDailyVolume10Day'),
                    'three_month_avg_volume': quote.get('averageDailyVolume3Month')
                }
                
                # Smart merge: only update if ticker already exists
                if ticker in financial_metrics_aggregate:
                    # Merge, preferring non-None values
                    for key, new_value in metrics_data.items():
                        if new_value is not None:
                            # New value is good, use it
                            financial_metrics_aggregate[ticker][key] = new_value
                        # else: keep existing value (even if it's None)
                    
                    # Same for price data
                    for key, new_value in price_data.items():
                        if new_value is not None:
                            if ticker not in price_modules_aggregate:
                                price_modules_aggregate[ticker] = {'price': {}}
                            price_modules_aggregate[ticker]['price'][key] = new_value
                else:
                    # First time seeing this ticker, just add it
                    financial_metrics_aggregate[ticker] = metrics_data
                    price_modules_aggregate[ticker] = {'price': price_data}
        
        logger.info(f"Extracted data for {len(financial_metrics_aggregate)} unique tickers from {len(screeners)} screeners")
        return (price_modules_aggregate, financial_metrics_aggregate)