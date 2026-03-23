from APIDataIO import APIDataIO
from YahooQueryService import YahooQueryService
from datetime import datetime, timedelta
import helpers
import logging


logger = logging.getLogger(__name__)


class TransactionManager(APIDataIO):
    """
    Handles Buy/Sell, Deposit/Withdraw, and supporting methods.

    Data flow:
        Fetch current price > show user their current holdings of the given stock as well as price data >
        on confirm fetch price agian > write tx to database

        Note: Price update daemon will be updating all holding prices in the background, no need to manually do this here.
    """

    def record_trade(self, tx_type: str, user_id, ticker, qty):
        """
    
        """
        # Get user's cash balance
        pass

    def check_can_afford(self, user_id, ticker, qty) -> bool:
        """
        Check if user can afford a tx.
        return balance if yes, return False or something if no.
        Assume stock has already been upserted into db
        """
        # Check input
        ticker = str(ticker).strip()

        # Check ticker's price
        overview = self.get_stock_basic_overview(ticker)
        if not overview or not isinstance(overview, dict):
            logger.warning(f"No data found for {ticker}. Transaction failed.")
            return False
        
        price = overview.get("last_price")
        # Calculate trade value
        tx_value = price * qty

        # Get user balance
        row = self.simple_query("SELECT cash FROM users WHERE id = ?", (user_id, ))
        balance = 0
        if row and isinstance(row, list):
            balance = row[0].get('cash', 0)
         
        # Compare
        if tx_value >= balance:
            return True
        else:
            return False

    def record_balance_snapshot(self):
        """
        """
        pass


    # What this needs to be
        # Record buy/sell to transactions table
        # Get info about user holdings of the relevant stock for the confirmation screen


