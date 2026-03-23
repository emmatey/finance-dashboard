from CommonQueries import CommonQueries
from YahooQueryService import YahooQueryService
from datetime import datetime, timedelta
import helpers
import logging


logger = logging.getLogger(__name__)


class TransactionManager(CommonQueries):
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

    def check_can_afford(self, user_id: int, ticker: str, qty: int) -> bool:
        """
        Check if user can afford a transaction.
        
        Args:
            user_id: User's ID
            ticker: Stock ticker symbol
            qty: Number of shares to buy
            
        Returns:
            True if user can afford the transaction, False otherwise
        """
        # Get current price (uses CommonQueries.get_stock_basic_overview)
        price = self.get_current_price(ticker)
        
        if not price:
            logger.warning(f"No price found for {ticker}. Transaction blocked.")
            return False
        
        # Calculate trade value
        tx_value = price * qty
        
        # Get user balance (uses CommonQueries.get_balance)
        balance = self.get_balance(user_id)
        
        if balance is None:
            logger.error(f"User {user_id} not found")
            return False
        
        if balance >= tx_value:
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


