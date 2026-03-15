import datetime
import logging
import pandas as pd
import yahooquery as yq
from ResearchDataCoordinator import ResearchDataCoordinator
from typing import List, Tuple, Dict, Union, Any, Optional
from YahooAPIClient import yq_exception_handler

logger = logging.getLogger(__name__)


class YahooQueryService:
    """
    Service layer for Yahoo Finance API interactions to support the /research route.

    Provides methods to fetch stock data, news, and financial metrics
    using yahooquery library.

    Attributes:
        ticker_factory: Callable that creates yahooquery Ticker instances
        search_factory: Callable that creates yahooquery Search instances
    """

    def __init__(
            self,
            ticker_factory = yq.Ticker,
            search_factory = yq.search,
            screener_factory = yq.Screener
            ) -> None:
        """
        Initialize the Yahoo Query Service.

        Args:
            ticker_factory: Factory function for creating Ticker instances (default: yq.Ticker)
            search_factory: Factory function for creating Search queries (default: yq.search)
        """
        self.ticker_factory = ticker_factory
        self.search_factory = search_factory
        self.screener_factory = screener_factory

    @yq_exception_handler()
    def yq_ticker_get_modules(
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

            "If only one module is retrieved, the structure will be flattened to:
            {symbol: {key: value}}, foregoing the 'module_name' level."

        Raises:
            ValueError: If symbols is not a string or list

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

        ticker = self.ticker_factory(symbols)
        raw_modules = ticker.get_modules(safe_modules)

        if not isinstance(raw_modules, dict):
            logger.warning(f"Yahoo API Error for {symbols}: {raw_modules}")
            return {}

        # Normalize single-module response structure.
        if len(safe_modules) == 1:
            module_name = safe_modules[0]
            return {symbol: {module_name: data} for symbol, data in raw_modules.items()}

        return raw_modules

    @yq_exception_handler()
    def yq_ticker_price_map(
        self,
        symbols: Union[List[str], str]
    ) -> Dict[str, Union[float, str, None]]:
        """
        Get current market prices for one or more stock symbols.

        Args:
            symbols: Single ticker symbol or list of symbols (e.g., 'AAPL' or ['AAPL', 'MSFT'])

        Returns:
            Dictionary mapping symbols to their current prices:
                {symbol: price} where price is:
                    - float: successful price retrieval
                    - str: error message from API
                    - None: price not available in response

        Example:
            >>> service.yq_ticker_price_map(['AAPL', 'MSFT'])
            {'AAPL': 150.25, 'MSFT': 380.50}
        """
        if isinstance(symbols, str):
            symbols = [symbols.upper()]
        else:
            symbols = [i.upper() for i in symbols]

        ticker = self.ticker_factory(symbols)
        result = ticker.price

        price_map: Dict[str, Union[float, str, None]] = {}
        for symbol, data in result.items():
            if isinstance(data, dict):
                # YQ returned data dict
                price = data.get("regularMarketPrice")
                price_map[symbol] = price
            else:
                # YQ returned error string or unexpected format
                logger.debug(f"Price fetch failed for {symbol}: {data}")
                price_map[symbol] = data

        return price_map
    
    @ResearchDataCoordinator.register_as_research('historical_prices', api=True)
    @yq_exception_handler()
    def yq_ticker_historical_prices(
        self,
        symbol: str,
        period: str = "5y",
        interval: str = "1d"
    ) -> Optional[List[Tuple[pd.Timestamp, float, int, str]]]:
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
                - date: pandas.Timestamp (timezone-aware UTC)
                - close: Adjusted close price (float)
                - volume: Trading volume (int)
                - symbol: Stock ticker
            Returns None if data retrieval fails or the DataFrame is empty.

        Reference:
            https://yahooquery.dpguthrie.com/guide/ticker/historical/
        """
        symbol = symbol.upper()
        ticker = self.ticker_factory(symbol)
        df = ticker.history(period=period, interval=interval, adj_ohlc=True, adj_timezone=False)

        if isinstance(df, pd.DataFrame) and not df.empty:
            # Flatten multidex
            df_flat = df.reset_index()

            # Select required data
            df_subset = df_flat[['date', 'close', 'volume', 'symbol']].copy()

            # Filter out any rows where ANY of the three target columns are empty
            df_filter = df_subset.dropna(subset=['date', 'close', 'volume', 'symbol'])

            # Convert to list of tuples
            data_tuples = df_filter.values.tolist()

            return [tuple(i) for i in data_tuples]

        else:
            logger.warning(f"Price retrieval error for {symbol}.")
            return None

    @ResearchDataCoordinator.register_as_research('stock_splits', api=True)
    @yq_exception_handler()
    def yq_ticker_stock_splits(
        self,
        symbols: Union[List[str], str],
        period: str = "5y"
    ) -> List[Tuple[pd.Timestamp, float, str]]:
        """
        Retrieve historical stock split data for one or more symbols.

        Args:
            symbols: Single ticker symbol or list of symbols
            period: Time period to search for splits
                   Options: ['1d', '5d', '7d', '60d', '1mo', '3mo', '6mo',
                            '1y', '2y', '5y', '10y', 'ytd', 'max']

        Returns:
            List of tuples containing (date, split_ratio, symbol)
            Returns empty list if no splits found or on error

        Example:
            >>> service.yq_ticker_stock_splits(['AAPL'])
            [(Timestamp('2020-08-31'), 4.0, 'AAPL'), ...]
        """
        if isinstance(symbols, str):
            symbols = [symbols.upper()]
        else:
            symbols = [i.upper() for i in symbols]

        t = self.ticker_factory(symbols)
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

        dates: List[pd.Timestamp] = splits['date'].tolist()
        split_ratios: List[float] = splits['splits'].tolist()
        symbols_list: List[str] = splits['symbol'].tolist()

        return list(zip(dates, split_ratios, symbols_list))

    @ResearchDataCoordinator.register_as_research('news', api=True)
    @yq_exception_handler()
    def yq_search_get_news(
        self,
        symbol: str,
        qty: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent news articles related to a stock symbol.

        Retrieves and filters the latest news stories, sorted by publish date.
        Extracts thumbnail URLs from nested response structure.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            qty: Maximum number of news items to return (default: 10)

        Returns:
            List of dictionaries, each containing:
                - uuid: Unique identifier for the article
                - title: Article headline
                - publisher: News source name
                - link: URL to full article
                - providerPublishTime: Unix timestamp (seconds since epoch)
                - thumbnail: URL of thumbnail image or "N/A"
                - relatedTickers: List of related stock symbols
            Returns empty list if no news found

        Note:
            News items are sorted by publish time (newest first) before
            being limited to qty items.
        """
        if not isinstance(symbol, str):
            raise ValueError(
                "'Symbol' paramater must be a string which represents a stock ticker. E.G APPL")

        response = self.search_factory(symbol.upper())

        # Extract news array from response
        data: List[Dict[str, Any]] = response.get('news', [])
        if not data:
            return []

        # Sort by publish date to extract the newest stories
        # Sorting by providerPublishTime in descending order (newest first)
        news_all = sorted(
            data,
            key=lambda item: item.get('providerPublishTime', 0),
            reverse=True
        )

        # Truncate to requested quantity
        news = news_all[:qty]

        # Filter to only relevant keys
        desired_keys = [
            'uuid', 'title', 'publisher', 'link',
            'providerPublishTime', 'thumbnail', 'relatedTickers'
        ]
        for story in news:
            for key in list(story.keys()):
                if key not in desired_keys:
                    del story[key]

        # Extract thumbnail URL from nested structure
        # Original structure: thumbnail: {resolutions: [{url, width, height, tag}, ...]}
        # Index 0 = full size, Index 1 = thumbnail size (120x120)
        for story in news:
            thumbnail_url = "N/A"

            resolutions = story.get("thumbnail", {})
            if resolutions:
                images = resolutions.get("resolutions", [])
                if images and len(images) > 1:
                    try:
                        # Prefer thumbnail-sized image at index 1
                        thumbnail_url = images[1].get("url", "N/A")
                    except (IndexError, AttributeError):
                        thumbnail_url = "N/A"

            story["thumbnail"] = thumbnail_url

        return news

    @ResearchDataCoordinator.register_as_research('financial_metrics', api=True, modules=['price', 'defaultKeyStatistics', 'summaryDetail', 'financialData'])
    def get_financial_metrics(
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

                # Valuation & Risk (defaultKeyStatistics module)
                "beta": defaultKeyStatistics.get('beta'),
                "eps": defaultKeyStatistics.get('trailingEps'),
                "trailing_pe": defaultKeyStatistics.get('trailingPE'),
                "forward_pe": defaultKeyStatistics.get('forwardPE'),
                "profit_margin": defaultKeyStatistics.get('profitMargins'),

                # Range & Yield (summaryDetail module)
                "dividend_yield": summaryDetail.get('dividendYield'),
                "fifty_two_week_high": summaryDetail.get('fiftyTwoWeekHigh'),
                "fifty_two_week_low": summaryDetail.get('fiftyTwoWeekLow'),

                # Analyst Sentiment & Health (financialData module)
                "rating": financialData.get('recommendationKey'),
                "target_price": financialData.get('targetMeanPrice'),
                "analyst_count": financialData.get('numberOfAnalystOpinions'),
                "current_ratio": financialData.get('currentRatio'),
                "debt_to_equity": financialData.get('debtToEquity')
            }
            out[symbol] = metrics

        return out

    @ResearchDataCoordinator.register_as_research('company_profile', api=True, modules=['summaryProfile'])
    def get_company_overview(
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
                "website": summaryProfile.get("website", "Unknown")
            }

            out[symbol] = company_data

        return out

    @ResearchDataCoordinator.register_as_research('insider_trades', api=True, modules=['insiderTransactions'])
    def get_insider_trades(
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

    @yq_exception_handler()
    def yq_screener_get_screeners(self,
                                  screeners: List[str] | str,
                                  count: int = 10
                                  ) -> Dict:
        """
        In the style of get_modules, query yahoo API for screener objects.

        Args: screeners: a list of the names of the screeners requested.

        Screener Format: https://yahooquery.dpguthrie.com/guide/screener/#get_screeners
        """
        # Clean input.
        safe_input = []
        if isinstance(screeners, str):
            safe_input.append(screeners.strip())
        elif isinstance(screeners, list):
            for i in screeners:
                safe_input.append(str(i).strip())
        else:
            raise ValueError(
                "yq_screener_get_screeners 'screeners' paramater must be a str, or list of strs which represent screener names.\n\
                https://yahooquery.dpguthrie.com/guide/screener/#get_screeners")
    
        # Call get_screeners
        s = self.screener_factory()
        screeners = s.get_screeners(safe_input, count)

        return screeners

    def _post_screen_screener_data(self, screeners):
        """
        Remove securities which dont meet the following criteria.
            1. 
        """
        pass

    def get_most_active_tickers(self, screeners: Dict) -> Dict:
        """
        Uses "most_active" screener to get the most traded tickers currently.

        Args: screeners, the data returned from get_screeners()

        Returns: 
        """
        pass
        # Extract required data from screeners arg.
            # Filter out the top 10
            # Filter for only equities
            # Filter for regularMarketPrice over one dollar
            # 
        # Format for db/io setter.
    
    def get_most_visited_tickers(self):
        """
        Uses "most_visited" screener to get most viewed tickers currently.
        """
        pass
    
    def get_day_gainers(self):
        """
        Uses "day_gainers" screener to get tickers with biggest positive price swing
        as a % of stock price today.
        """ 
        pass
        
    def get_day_losers(self):
        """
        Uses "day_losers" screener to get tickers with biggest negative price swing
        as a % of stock price today.
        """
        pass

    def get_relative_volumes(self):
        """
        Find the stocks with the largest spikes in relative trade volume.
        """
        # averageDailyVolume3Month
        # vs regularMarketVolume
        pass