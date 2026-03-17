from DbManager import DbManager
from APIDataIO import APIDataIO
from YahooQueryService import YahooQueryService
from datetime import datetime, timedelta
import helpers
import logging


logger = logging.getLogger(__name__)


class TransactionManager(DbManager):
    """
    Handles Buy/Sell, Deposit/Withdraw, and supporting methods.

    Attributes:
        yq_service: YahooQueryService instance for API interactions
    """

    def __init__(self, yq_service=YahooQueryService()):
        """
        Initialize TransactionManager with Yahoo Query Service.

        Args:
            yq_service: Instance of YahooQueryService for fetching stock data
        """
        self.yq_service = yq_service

    @staticmethod
    def filter_user_symbol_query(symbol: str) -> str:
        """
        Strip out all non alphanum chars and symbols from search terms.
        """
        if type(symbol) is not str:
            logger.warning(
                f"{symbol} is of invalid type. {type(symbol)} is not string. Returning empty str.")
            return ""

        buffer = []
        for char in symbol:
            if char.isalnum():
                buffer.append(char)

        return ''.join(buffer).upper()

    def exists_in_db(self, symbol: str) -> dict | None:
        """
        Check if symbol exists in the local database.

        Returns:
            Dictionary with symbol data including last_updated timestamp if found,
            None if not found
        """
        query = self.simple_query(
            "SELECT ticker, last_updated FROM symbols WHERE ticker = ?",
            (symbol,)
        )
        if query:
            logger.debug(f"Symbol {symbol} found in DB")
            return query[0]  # type: ignore # Return the row dict
        else:
            logger.debug(f"Symbol {symbol} not in DB")
            return None

    def exists_online(self, symbol: str) -> dict | None:
        """
        Check if symbol exists online using YahooQueryService.

        Args:
            symbol: Stock ticker symbol

        Returns:
            The price module data payload if found, otherwise None.
        """
        try:
            # Use the protected yq_ticker_get_modules method to get price module
            modules = self.yq_service.yq_ticker_get_modules(symbol, 'price')

            if not modules:
                logger.warning(f"{symbol} not found via YahooQueryService.")
                return None

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
                return fallback

            logger.warning(f"{symbol} also not found on backup datasource.")
            return None

        except Exception as e:
            logger.exception(f"Error checking {symbol} online:")
            return None

    def verify_symbol(self, symbol: str) -> bool:
        """
        Verify that a symbol is valid and tradeable.

        Uses a 24-hour cache strategy to minimize API calls:
        - If symbol is in DB and last_updated < 24 hours: trust it (return True)
        - If symbol is in DB but stale (>= 24 hours): verify online and update
        - If symbol not in DB: check online and insert if found

        Args:
            symbol: Stock ticker symbol to verify

        Returns:
            True if symbol is valid and tradeable, False otherwise

        Behavior:
            - Logs critical warning if symbol exists in DB but can't be found online
            - Does NOT modify is_active status (that column has been removed)
            - Automatically upserts fresh data when found online
        """
        symbol = self.filter_user_symbol_query(symbol)

        # Check if symbol exists in DB
        db_result = self.exists_in_db(symbol)

        if db_result:
            # Symbol exists in DB - check if data is fresh
            last_updated_str = db_result.get('last_updated', "1970-01-01 00:00:01")

            # Parse the last_updated timestamp
            # SQLite returns datetime strings in format: 'YYYY-MM-DD HH:MM:SS'
            try:
                last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S')
                time_since_update = datetime.now() - last_updated

                # If data is fresh (< 24 hours), trust it
                if time_since_update < timedelta(hours=24):
                    logger.info(f"{symbol} found in DB and recently verified (updated {time_since_update} ago)")
                    return True

                # Data is stale (>= 24 hours) - verify online
                logger.debug(f"{symbol} in DB but stale (updated {time_since_update} ago). Verifying online...")

            except ValueError:
                # If timestamp parsing fails, treat as stale and verify online
                logger.warning(f"Could not parse last_updated timestamp for {symbol}. Verifying online...")

            # Check if symbol still exists online
            api_data = self.exists_online(symbol)

            if api_data:
                # Found online - update with fresh data
                logger.info(f"{symbol} verified online. Updating DB with fresh data.")
                APIDataIO().upsert_symbols(symbol, api_data)
                return True
            else:
                # Was in DB but NOT found online - potential delisting/renaming
                logger.critical(
                    f"MANUAL REVIEW NEEDED: {symbol} exists in database but could not be found online. "
                    f"This may indicate the symbol has been delisted, renamed, or there is an API issue. "
                    f"Last updated: {last_updated_str}"
                )
                return False

        else:
            # Symbol not in DB - check if it exists online
            logger.debug(f"{symbol} not in DB. Checking online...")
            api_data = self.exists_online(symbol)

            if api_data:
                # Found online - insert into DB
                logger.info(f"{symbol} found online. Adding to database.")
                APIDataIO().upsert_symbols(symbol, api_data)
                return True
            else:
                # Not in DB and not found online - invalid symbol
                logger.warning(f"{symbol} invalid. Not found locally nor online.")
                return False

    def record_buy_order_in_transactions_table(self, ):
        """
        Query db to record a buy after prior verification.


        """
        pass

    def write_pending_transaction_to_session(self, session, tx_type: str):
        """

        """
        pass

    ## Buy route ##
    # Verify symbol exists - Done
        # if exists but not in db, call insert funciton. DONE
    # Calculate purchase price - Can be done in route
        #
    # Check user can afford - Can be done with balance func (exists) - purchase price calculated
    # Record order in session token with age

    # Redirect to confirmation screen!
        # Render transaction data
        # Fetch new price from DB (updated by daemnon every 60 seconds globally)
        # System to fetch updated data

    # Recirect to confirm route
        # fetch new price from DB
        # Write to transactions -
        # balance snapshot
        # redirect home
