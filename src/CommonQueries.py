from DbManager import DbManager
import logging

logger = logging.getLogger(__name__)

class CommonQueries(DbManager):
    """
    Common database queries used across multiple managers.
    
    These are simple SELECT/UPDATE queries with no business logic.
    Complex queries with joins, CTEs, or business logic belong in
    their specific manager classes.
    """
    
    def get_balance(self, user_id: int):
        """
        Returns user's cash balance.

        Args:
            user_id: The user's ID

        Returns:
            User's cash balance as float, or None if user not found
        """
        sql = "SELECT cash FROM users WHERE id = ?"
        res = self.simple_query(sql, (user_id,))
        
        if not isinstance(res, list) or not res:
            return None
        return res[0]['cash']
    
    def update_user_cash(self, user_id: int, new_balance: float) -> bool:
        """
        Update user's cash balance. Returns True on success.
        """
        rows = self.simple_query(
            """
            UPDATE users
            SET cash = ?
            WHERE id = ?
            """, (new_balance, user_id)
        )
        if rows:
            return True
        else:
            return False

    def get_username_from_user_id(self, user_id: int) -> str | None:
        """
        Get username from user_id
        """
        sql = """
        SELECT username FROM users WHERE id = ?
        """
        result = self.simple_query(sql , (user_id,))
        assert isinstance(result, list)

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
        result = self.simple_query(sql, (username.strip(),))
        assert isinstance(result, list)

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
        result = self.simple_query(sql, (ticker,))
        assert isinstance(result, list)
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
        rows = self.simple_query(sql, (safe_query, ))

        if rows and isinstance(rows, list):
            return rows[0]
        else:
            logger.info(f"No data found locally for {safe_query}.")
            return None
        
    def get_current_price(self, symbol: str) -> float | None:
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