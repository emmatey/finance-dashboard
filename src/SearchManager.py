from DbManager import DbManager
from APIDataIO import APIDataIO
from YahooQueryService import YahooQueryService
from datetime import datetime, timedelta
import helpers
import logging


logger = logging.getLogger(__name__)

class SearchManager(DbManager):
    """
    Handle the search bar.
    Should show a union of db results and yq.search results in a search results page unless user types an exact match.
    In which case user should be directed right to the page in question.
    """
    def __init__(self, yq_service=YahooQueryService()):
        """
        Initialize TransactionManager with Yahoo Query Service.

        Args:
            yq_service: Instance of YahooQueryService for fetching stock data
        """
        self.yq_service = yq_service
        
    def exists_in_db(self, query: str):
        """
        Return the companies that are close to or the same as what the user is typing.
        """
        # Convert user input to string and add 'LIKE' wildcards.
        safe_query = f"%{str(query)}%"

        sql = """
        SELECT *
        FROM symbols 
        WHERE ticker LIKE ?
        OR company_name LIKE ?
        LIMIT 15
        """
        rows = self.simple_query(sql, tuple([safe_query, safe_query]))

        if rows:
            return rows
        else:
            logger.info(f"No data found for {query}")
            return None

    def exists_online(self, symbol: str) -> dict | bool:
        """
        Check if symbol exists online using YahooQueryService.

        Args:
            symbol: Stock ticker symbol

        Returns:
            The price module data payload if found, otherwise None.
        """
        try:
            modules = self.yq_service.yq_ticker_fetch_modules(symbol, 'price')

            if not modules:
                logger.warning(f"{symbol} not found via YahooQueryService.")
                return False

            # Extract price module for this symbol
            price_module = modules.get(symbol, {}).get('price', {})

            # Check for a valid dictionary with actual price data
            if isinstance(price_module, dict) and "regularMarketPrice" in price_module:
                logger.info(f"Symbol {symbol} found online via YahooQuery!")
                return price_module

            # If YahooQuery failed, check the CS50 fallback
            logger.warning(f"{symbol} not found on YahooQuery. Checking CS50.io...")
            fallback = helpers.lookup(symbol)

            if fallback:
                logger.info(f"Symbol {symbol} found online via backup datasource!")
                return True

            logger.warning(f"{symbol} also not found on backup datasource.")
            return False

        except Exception as e:
            logger.exception(f"Error checking {symbol} online:")
            return False