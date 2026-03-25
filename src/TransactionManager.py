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
        Record buy transaction, update cash balance.

        This method assumes:
        - User can afford the trade (checked by check_can_afford beforehand)
        - Symbol exists in DB (upserted by route handler)
        - Prices are current (updated by daemon)

        Args:
            user_id: User's ID
            ticker: Stock ticker symbol
            qty: Number of shares to buy (positive integer)

        Returns:
            True on success, False on failure
        """
        ticker = ticker.upper().strip()

        # Get current state
        balance = self.get_balance(user_id)
        if balance is None:
            logger.error(f"User {user_id} not found - cannot record buy")
            return False

        unit_price = self.get_current_price_from_db(ticker)
        if unit_price is None:
            logger.error(f"Price not available for {ticker} - cannot record buy")
            return False

        symbol_id = self.get_symbol_id(ticker)
        if symbol_id is None:
            logger.error(f"Symbol {ticker} not found in DB - cannot record buy")
            return False

        # Calculate new balance
        tx_value = unit_price * qty
        new_balance = round(balance - tx_value, 2)

        try:
            with self.get_db() as con:
                # Record transaction
                sql = """
                INSERT INTO transactions (user_id, symbol_id, transaction_type, qty, unit_price, cash_after)
                VALUES (?, ?, 'buy', ?, ?, ?)
                """
                con.execute(sql, (user_id, symbol_id, qty, unit_price, new_balance))

                # Update user's cash balance
                sql = """
                UPDATE users
                SET cash = ?
                WHERE id = ?
                """
                con.execute(sql,(new_balance, user_id))
        except Exception as e:
            logger.exception(f"Failed to record buy for user {user_id}: {e}")
            return False
        
        logger.info(
                    f"BUY recorded: User {user_id} bought {qty} shares of {ticker} "
                    f"at ${unit_price:.2f} (total: ${tx_value:.2f}). "
                    f"Cash: ${balance:.2f} → ${new_balance:.2f}"
                )
        return True
        
    def record_sell(self, user_id: int, ticker: str, qty: int) -> bool:
        """
        Record sell transaction, update cash balance.

        This method assumes:
        - User owns enough shares (checked by check_can_sell beforehand)
        - Symbol exists in DB
        - Prices are current (updated by daemon)

        Args:
            user_id: User's ID
            ticker: Stock ticker symbol
            qty: Number of shares to sell (positive integer)

        Returns:
            True on success, False on failure
        """
        ticker = ticker.upper().strip()

        # Get current state
        balance = self.get_balance(user_id)
        if balance is None:
            logger.error(f"User {user_id} not found - cannot record sell")
            return False

        unit_price = self.get_current_price_from_db(ticker)
        if unit_price is None:
            logger.error(f"Price not available for {ticker} - cannot record sell")
            return False

        symbol_id = self.get_symbol_id(ticker)
        if symbol_id is None:
            logger.error(f"Symbol {ticker} not found in DB - cannot record sell")
            return False

        # Calculate new balance (selling adds cash)
        tx_value = unit_price * qty
        new_balance = round(balance + tx_value, 2)

        try:
            with self.get_db() as con:
                # Record transaction.
                sql = """
                INSERT INTO transactions (user_id, symbol_id, transaction_type, qty, unit_price, cash_after)
                VALUES (?, ?, 'sell', ?, ?, ?)
                """
                con.execute(sql, (user_id, symbol_id, (qty * -1), unit_price, new_balance))

                # Update user's cash balance
                sql = """
                    UPDATE users
                    SET cash = ?
                    WHERE id = ?
                    """
                con.execute(sql, (new_balance, user_id))
        except Exception as e:
            logger.exception(f"Failed to record sell for user {user_id}: {e}")
            return False

        logger.info(
                    f"SELL recorded: User {user_id} sold {qty} shares of {ticker} "
                    f"at ${unit_price:.2f} (total: ${tx_value:.2f}). "
                    f"Cash: ${balance:.2f} → ${new_balance:.2f}"
                )
        return True

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

    def check_can_sell(self, user_id: int, ticker: str, qty: int) -> bool:
        """
        Check if the user owns enough of the stock they're trying to sell.

        Returns True if they do, and False otherwise.
        """
        # Normalize ticker
        ticker = str(ticker).upper().strip()

        # Get ticker_id
        self.get_symbol_id(ticker)
        
        # Check qty of ownership
        self.select_query("")
        # Compare to qty of sale
    