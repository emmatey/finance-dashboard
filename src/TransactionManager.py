from CommonQueries import CommonQueries
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

    def record_buy(self, user_id: int, ticker: str, qty: float) -> dict | None:
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
            return None

        unit_price = self.get_current_price_from_db(ticker)
        if unit_price is None:
            logger.error(f"Price not available for {ticker} - cannot record buy")
            return None

        symbol_id = self.get_symbol_id(ticker)
        if symbol_id is None:
            logger.error(f"Symbol {ticker} not found in DB - cannot record buy")
            return None

        # Calculate new balance
        tx_value = float(unit_price) * float(qty)
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
                SET cash = cash - ?
                WHERE id = ?
                """
                con.execute(sql,(tx_value, user_id))
        except Exception as e:
            logger.exception(f"Failed to record buy for user {user_id}: {e}")
            return None
        
        info_str = f"""BUY recorded: User {user_id} bought {qty} shares of {ticker}.
            at ${unit_price:.2f} (total: ${tx_value:.2f}). 
            Cash: ${balance:.2f} → ${new_balance:.2f}
        """
        logger.info(info_str)

        return {
            "success": True,
            "ticker": ticker,
            "qty": qty,
            "unit_price": unit_price,
            "tx_value": tx_value,
            "new_balance": new_balance
        }
        
    def record_sell(self, user_id: int, ticker: str, qty: float) -> bool:
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
                    SET cash = cash + ?
                    WHERE id = ?
                    """
                con.execute(sql, (tx_value, user_id))
        except Exception as e:
            logger.exception(f"Failed to record sell for user {user_id}: {e}")
            return False

        logger.info(
                    f"SELL recorded: User {user_id} sold {qty} shares of {ticker} "
                    f"at ${unit_price:.2f} (total: ${tx_value:.2f}). "
                    f"Cash: ${balance:.2f} → ${new_balance:.2f}"
                )
        return True

    def record_balance_snapshot(self, user_id: int) -> bool:
        """
        Record a balance snapshot for a single user.
        To be used after every buy and sell order.
        """
        cash_balance = self.get_balance(user_id)
        if cash_balance is None:
            logger.error(f"Cannot snapshot user {user_id} - user not found")
            return False
        # portfolio_value returns 0.0 if no holdings.
        portfolio_value = self.get_single_user_holdings_value(user_id)

        sql = """
        INSERT INTO balance_snapshots (user_id, portfolio_value, cash_balance)
        VALUES (?, ?, ?)
        """
        rows = self.modify_query(sql, (user_id, portfolio_value, cash_balance))
        if rows:
            logger.info(f"Balance snapshot recorded for user #{user_id}!")
            logger.info(f"Cash balance = {cash_balance} Portfolio value = {portfolio_value}")
            return True
        else:
            logger.warning(f"Balance snapshot for user #{user_id} failed!")
            return False
        
    def check_can_afford(self, user_id: int, ticker: str, qty: float) -> bool:
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
        tx_value = float(price) * float(qty)
        
        # Get user balance
        balance = self.get_balance(user_id)
        if balance is None:
            logger.error(f"User {user_id} not found")
            return False
        
        if balance >= tx_value:
            return True
        else:
            logger.warning(f"User {user_id} has Insufficient funds. Balance is {balance}, but {tx_value} is required.")
            return False

    def check_can_sell(self, user_id: int, ticker: str, qty: float) -> bool:
        """
        Check if the user owns enough of the stock they're trying to sell.

        Returns True if they do, and False otherwise.
        """
        # Normalize ticker
        ticker = str(ticker).upper().strip()

        # Check qty of ownership
        record = self.get_holding_info_per_user(user_id=user_id, ticker=ticker)
        qty_owned = 0
        if isinstance(record, dict):
            qty_owned = record.get("qty_owned", 0)

        # Compare to qty of sale
        if qty_owned < qty:
            return False
        return True