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

    def record_buy(self, user_id: int, ticker: str, qty: int) -> bool:
        """
        Record buy in transactions table, update cash balance, and take balance snapshot.

        This method assumes the user can afford the trade, 
        the prices are up to date, and the symbol already exists in the db.
        """
        # Get user's cash balance
        balance = self.get_balance(user_id)

        # Get ticker's price
        unit_price = self.get_current_price_from_db(ticker)

        # Calculate tx value
        if not unit_price:
            logger.error(f"Warning! Recording of buy transaction failed for {ticker} userID: {user_id}")
            return False
        
        tx_value = unit_price * qty

        # Update user's cash balance
        new_balance = round(balance - tx_value, 2)
        self.update_user_cash(user_id, new_balance)

        # Write to transactions
        sql = """
        INSERT INTO transactions (user_id, symbol_id, transaction_type, qty, unit_price, cash_after)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.modify_query(sql, (user_id, self.get_symbol_id(ticker), 'buy', qty, unit_price, new_balance))
        
        logger.info(f"Record buy for user #{user_id} for {qty} shares of {ticker} at {unit_price}. Their cash blanace is now {new_balance}")
        return True

    def record_sell(self, user_id: int, ticker: str, qty: int) -> bool:
        """
        Record sell in transactions table, update cash balance, and take balance snapshot.

        This method assumesthe prices are up to date.
        """
        # Get user's cash balance
        balance = self.get_balance(user_id)

        # Get ticker's price
        ticker_price = self.get_current_price_from_db(ticker)

        # Update user's cash balance
        

        # Write to transactions

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
        # Get current price
        price = self.get_current_price_from_db(ticker)
        
        if not price:
            logger.warning(f"No price found for {ticker}. Transaction blocked.")
            return False
        
        # Calculate trade value
        tx_value = price * qty
        
        # Get user balance
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


