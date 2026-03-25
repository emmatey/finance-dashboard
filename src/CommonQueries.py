from collections import defaultdict
from DbManager import DbManager
import logging
import math

logger = logging.getLogger(__name__)

class CommonQueries(DbManager):
    """
    Common database queries used across multiple managers.
    
    These are simple SELECT/UPDATE queries with no business logic.
    Complex queries with joins, CTEs, or business logic belong in
    their specific manager classes.
    """
    
    def get_balance(self, user_id: int) -> float | None:
        """
        Returns user's cash balance.

        Args:
            user_id: The user's ID

        Returns:
            User's cash balance as float, or None if user not found
        """
        sql = "SELECT cash FROM users WHERE id = ?"
        res = self.select_query(sql, (user_id,))
        
        if not res:
            logger.warning(f"Balance inquiry failed for {user_id}")
            return None
        return res[0]['cash']

    def get_username_from_user_id(self, user_id: int) -> str | None:
        """
        Get username from user_id
        """
        sql = """
        SELECT username FROM users WHERE id = ?
        """
        result = self.select_query(sql , (user_id,))

        if result:
            return result[0]['username']
        else:
            return None
    
    def get_user_id_from_username(self, username: str) -> int | None:
        """
        Get user_id from username
        """
        sql = """
        SELECT id
        FROM users
        WHERE username = ?
        """
        result = self.select_query(sql, (username.strip(),))

        if result:
            return result[0]['id']
        else:
            return None
    
    def get_symbol_id(self, ticker: str) -> int | None:
        """
        Get symbol database ID from ticker
        """
        ticker = ticker.upper().strip()
        sql = """
        SELECT id
        FROM symbols
        WHERE ticker = ?
        """
        result = self.select_query(sql, (ticker,))
        if result:
            return result[0]['id']
        else:
            return None
    
    def get_stock_basic_overview(self, symbol: str):
        """
        Retrieve data from the symbols table about a given holding.
        """
        # Convert user input to string.
        safe_query = str(symbol).upper()

        sql = f"""
        SELECT *
        FROM symbols 
        WHERE ticker = ?
        """
        rows = self.select_query(sql, (safe_query, ))

        if rows:
            return rows[0]
        else:
            logger.info(f"No data found locally for {safe_query}.")
            return None
        
    def get_current_price_from_db(self, symbol: str) -> float | None:
        """
        Returns the current price of a given symbol.
        """
        res = self.get_stock_basic_overview(symbol)
        if not res:
            return None
        else:
            return res.get('last_price')
        
    def symbol_exists_in_db(self, symbol: str) -> bool:
        """
        Checks if a symbol exists in the db.
        """
        res = self.get_stock_basic_overview(symbol)
        if res:
            return True
        else:
            return False
    
    def calculate_holdings(self, user_id: int = 0, all_users: bool = False):
        """
        Calculate holdings values and qtys for one or all users.

        Args:
            user_id: The user's ID (ignored if all_users=True)
            all_users: If True, calculate for all users

        Returns:
            Dictionary mapping user_id to portfolio value: {user_id: value}
            Dictionary mapping user_id to holdings id's and their quantaties.

        Raises:
            ValueError: If all_users is False and user_id is 0
        """
        tx_history_company_grouped = self.get_transaction_history(user_id=user_id, all_users=all_users)


        # Query updated prices
        symbols = list(tx_history_company_grouped.keys())
        if not symbols:
            logger.debug("No holdings found for user(s). Returning empty result.")
            return {}
        
        placeholders = ", ".join(['?' for _ in symbols])
        sql = f"""
        SELECT id, last_price 
        FROM symbols
        WHERE id IN ({placeholders})
        """
        price_rows = self.select_query(sql, tuple(symbols))
        if not price_rows:
            logger.error("Failed to fetch prices.")
            return {}
        price_map = {row['id']: row['last_price'] for row in price_rows}

        # Group by user
        user_grouped = defaultdict(list)
        for history in tx_history_company_grouped.values():
            for tx in history:
                user_grouped[tx.get('user_id')].append(tx)

        # Calculate holdings value
        holdings_value_per_user = {}
        holdings_per_user = {}
        for user, history in user_grouped.items():
            user_shares = defaultdict(float)
            for tx in history:
                user_shares[tx['symbol_id']] += tx['qty']

            current_value = sum(qty * price_map.get(symbol_id, 0) for symbol_id, qty in user_shares.items())
            holdings_value_per_user[user] = round(current_value, 2)
            holdings_per_user[user] = user_shares

        return holdings_value_per_user, holdings_per_user
    
    def get_transaction_history(self, user_id: int = 0, all_users: bool = False) -> dict[int, list[dict]]:
        """
        Query transaction history, grouped by symbol_id.
        Returns only active holdings, split-adjusted.
    
        Args:
            user_id: The user's ID. Required if all_users is False.
            all_users: If True, fetch transactions for all users.
    
        Returns:
            Dict of {symbol_id: [transactions]} where each transaction contains:
            transaction_id, user_id, symbol_id, transaction_type,
            qty, unit_price, date (unix timestamp).
            Zero-quantity holdings are excluded.
            Quantities and prices are adjusted for stock splits.
    
        Raises:
            ValueError: If all_users is False and user_id is 0
        """
        if user_id == 0 and all_users is False:
            logger.error("get_transaction_history called without user_id and all_users=False")
            raise ValueError("If all_users is false, a user ID is required.")

        base_sql = """
            SELECT transaction_id, user_id, symbol_id, transaction_type, qty, unit_price, unixepoch(transaction_datetime) AS date
            FROM transactions
        """
        if all_users:
            tx_sql = base_sql + " ORDER BY transaction_datetime"
            params = ()
        else:
            tx_sql = base_sql + " WHERE user_id = ? ORDER BY transaction_datetime"
            params = (user_id,)

        tx_query = self.select_query(tx_sql, params)

        # Group transactions by symbol.
        grouped = defaultdict(list)
        for tx in tx_query:
            grouped[tx.get('symbol_id')].append(tx)
        
        trimmed = self._delete_holdings_with_zero_quantity(grouped)
        split_adjusted = self._adjust_for_stock_splits(trimmed)

        return split_adjusted
        
    def get_single_user_holdings_value(self, user_id: int) -> float:
        """
        Sum the current market value of a single user's holdings.

        Args:
            user_id: The user's ID

        Returns:
            Total portfolio value as float, or 0.0 if no holdings
        """
        holdings_value_per_user, holdings_per_user = self.calculate_holdings(user_id=user_id, all_users=False)
        return holdings_value_per_user.get(user_id, 0.0)

    def get_all_users_holdings_values(self) -> dict[int, float]:
        """
        Sum the current market value of all users' holdings.
        Used by daemon for midnight balance snapshots.

        Returns:
            Dictionary mapping user_id to portfolio value: {user_id: value}
        """
        holdings_value_per_user, holdings_per_user = self.calculate_holdings(user_id=0, all_users=True)

        return holdings_value_per_user

    def get_holding_qty_value_per_user(self, user_id: int, ticker: str) -> dict | None:
        """
        Get quantity and current value of a specific stock holding for a user.

        Args:
            user_id: User's ID
            ticker: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dict with keys: user_id, ticker, ticker_id, current_price, qty_owned, holding_value
            Returns None if:
                - User has no holdings
                - Ticker not found in database
                - User doesn't own this ticker
                - Price not available

        Example:
            >>> rm = ReportManager()
            >>> holding = rm.get_holding_qty_value_per_user(1, 'AAPL')
            >>> print(holding)
            {'user_id': 1, 'ticker': 'AAPL', 'ticker_id': 5, 
             'current_price': 150.25, 'qty_owned': 10, 'holding_value': 1502.50}
        """
        ticker = ticker.upper().strip()

        # Get this user's holdings (not all users!)
        _, holdings_per_user = self.calculate_holdings(user_id=user_id, all_users=False)

        user_holdings = holdings_per_user.get(user_id)
        if not user_holdings:
            logger.debug(f"User {user_id} has no holdings")
            return None

        # Get ticker info from DB
        ticker_info = self.select_query("""
            SELECT id, last_price
            FROM symbols
            WHERE ticker = ?
        """, (ticker,))
        if not ticker_info:
            logger.warning(f"Ticker {ticker} not found in database")
            return None

        ticker_id = ticker_info[0]['id']
        current_price = ticker_info[0]['last_price']

        if current_price is None:
            logger.warning(f"Price not available for {ticker}")
            return None

        # Check if user owns this ticker
        qty_owned = user_holdings.get(ticker_id, 0)

        if qty_owned == 0:
            logger.debug(f"User {user_id} does not own {ticker}")
            return None

        return {
            'user_id': user_id,
            'ticker': ticker,
            'ticker_id': ticker_id,
            'current_price': current_price, 
            'qty_owned': qty_owned,
            'holding_value': round(current_price * qty_owned, 2)
        }

    def _adjust_for_stock_splits(self, transaction_history):
        """
        Adjust transaction history based on stock splits.
        Each transaction must be adjusted for all splits from transaction date -> now.

        Args:
            transaction_history: Dict of {symbol_id: [transactions]}

        Returns:
            Dict of {symbol_id: [adjusted_transactions]} with qty and unit_price
            adjusted for all stock splits that occurred after each transaction
        """
        # Query for stock splits
        symbol_ids = list(transaction_history.keys())
        if not symbol_ids:
            return transaction_history
        
        placeholders = ", ".join(['?' for _ in symbol_ids])
        sql = f"SELECT symbol_id, unixepoch(split_date) AS date, split_ratio AS ratio FROM stock_splits WHERE symbol_id IN ({placeholders})"
        query = self.select_query(sql, tuple(symbol_ids))
        
        if not query:
            logger.debug("_adjust_for_stock_splits: no splits found")
            return transaction_history

        # Format for easier lookup: {symbol_id: [{splits}]}
        split_history = defaultdict(list)
        for row in query:
            split_history[row.get('symbol_id')].append(row)

        # For each split newer than the transaction, multiply qty and divide price by split_ratio
        for symbol_id, transactions in transaction_history.items():
            splits = split_history.get(symbol_id)
            if not splits:
                continue

            for tx in transactions:
                transaction_date = tx.get("date")

                for split in splits:
                    if transaction_date < split.get('date'):
                        split_ratio = float(split.get("ratio"))
                        if split_ratio <= 0:
                            logger.error(f"Invalid split ratio for symbol {symbol_id}: {split}")
                            continue
                        tx['qty'] *= split_ratio
                        tx['unit_price'] /= split_ratio

        return transaction_history
    
    def _delete_holdings_with_zero_quantity(
        self, transaction_history):
        """
        Remove the record of holdings the user no longer owns to avoid calculating
        extra stock splits needlessly, and to format the data for later display.

        Args:
            transaction_history: Dict of {symbol_id: [transactions]}

        Returns:
            Filtered dict with zero-quantity holdings removed
        """
        empty = []
        for stock_id, tx_history in transaction_history.items():
            qty = 0
            for tx in tx_history:
                # Db rule: sell orders have negative qty
                qty += tx.get('qty', 0)
            if math.isclose(qty, 0.0, abs_tol=1e-5):
                empty.append(stock_id)

        for stock_id in empty:
            del transaction_history[stock_id]

        return transaction_history