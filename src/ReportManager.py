import logging
import math
from DbManager import DbManager
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple, Union, Any


logger = logging.getLogger(__name__)

class ReportManager(DbManager):
    """
    Handles displaying information about user. I.e holdings, transaction history, account balance/grand total

    Read from DB, format for frontend.
    """

    def get_balance(self, user_id: int) -> Optional[float]:
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

    def get_all_users_holdings_values(self) -> Dict[int, float]:
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
        ticker_info = self.simple_query("""
            SELECT id, last_price
            FROM symbols
            WHERE ticker = ?
        """, (ticker,))

        if not ticker_info:
            logger.warning(f"Ticker {ticker} not found in database")
            return None

        assert not isinstance(ticker_info, int)

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
        if user_id == 0 and all_users is False:
            logger.error("_calculate_holdings_value called without user_id and all_users=False")
            raise ValueError("If all_users is false, a user ID is required.")

        base_sql = """
            SELECT user_id, symbol_id, transaction_type, qty, unit_price, unixepoch(transaction_datetime) AS date
            FROM transactions
        """
        if all_users:
            tx_sql = base_sql + " ORDER BY transaction_datetime"
            params = ()
        else:
            tx_sql = base_sql + " WHERE user_id = ? ORDER BY transaction_datetime"
            params = (user_id,)

        tx_query = self.simple_query(tx_sql, params)
        
        if not isinstance(tx_query, list):
            logger.warning("_calculate_holdings_value: no transactions found")
            return {}

        # Group by symbol_id
        symbol_id_grouped = defaultdict(list)
        for row in tx_query:
            symbol_id_grouped[row.get('symbol_id')].append(row)

        # Adjust for splits
        adjusted = self._adjust_for_stock_splits(symbol_id_grouped)

        # Query updated prices
        symbols = list(adjusted.keys())
        if not symbols:
            logger.debug("No holdings found for user(s). Returning empty result.")
            return {}
        
        placeholders = ", ".join(['?' for _ in symbols])
        price_rows = self.simple_query(f"SELECT id, last_price FROM symbols WHERE id IN ({placeholders})", tuple(symbols))
        
        if not isinstance(price_rows, list):
            logger.error("_calculate_holdings_value: failed to fetch prices")
            return {}
            
        price_map = {row['id']: row['last_price'] for row in price_rows}

        # Group by user
        user_grouped = defaultdict(list)
        for history in adjusted.values():
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

    def get_portfolio_view(self, user_id: int) -> List[Dict[str, Union[str, float]]]:
        """
        Returns data ready to be displayed on front page.

        Args:
            user_id: The user's ID

        Returns:
            List of dictionaries, each containing:
                - symbol: Ticker symbol
                - name: Company name
                - shares: Number of shares owned (split-adjusted)
                - unit_price: Current market price per share
                - cost_basis: Average cost per share (FIFO)
                - current_value: Total current value (shares * unit_price)
                - total_cost: Total amount paid for shares
                - gain_loss: Dollar gain/loss (current_value - total_cost)
                - gain_loss_pct: Percentage gain/loss
            Sorted by current_value descending
        """
        raw_history = self.get_transaction_history_per_user(user_id)
        trimmed_history = self._delete_holdings_with_zero_quantity(raw_history)
        adjusted_history = self._adjust_for_stock_splits(trimmed_history)
        cost_basis_data = self._get_cost_basis(adjusted_history)

        # Query db for all stocks at once to avoid the so called 'N+1 queries' problem.
        # https://planetscale.com/blog/what-is-n-1-query-problem-and-how-to-solve-it
        stock_ids = list(adjusted_history.keys())
        if not stock_ids:
            logger.debug(f"No portfolio holdings for user_id={user_id}")
            return []
        
        placeholders = ', '.join(['?' for _ in stock_ids])
        sql = f"SELECT id, ticker, company_name, last_price FROM symbols WHERE id IN ({placeholders})"
        query_raw = self.simple_query(sql, tuple(stock_ids))
        
        if not isinstance(query_raw, list):
            logger.error(f"get_portfolio_view: failed to fetch symbols for user_id={user_id}")
            return []
            
        query_formatted = {line.get('id'): line for line in query_raw}

        # Format the data to have one line item per holding which conforms to '/index' interface
        index_view = []
        for stock_id, tx_history in adjusted_history.items():
            query = query_formatted.get(stock_id, {})
            if not query:
                logger.error(f"Data integrity error: symbol_id {stock_id} not found in symbols table")
                continue

            shares = sum(tx.get('qty', 0) for tx in tx_history)
            unit_price = query.get('last_price', 0)
            basis_info = cost_basis_data.get(stock_id, {})
            cost_basis = basis_info.get('cost_basis', 0)
            total_cost = basis_info.get('total_cost', 0)
            current_value = shares * unit_price

            # Calculate gain/loss
            gain_loss = current_value - total_cost
            gain_loss_pct = (gain_loss / total_cost * 100) if total_cost > 0 else 0

            line = {
                'symbol': query.get('ticker', f'ERROR in holding {stock_id}'),
                'name': query.get('company_name', f'ERROR in holding {stock_id}'),
                'shares': shares,
                'unit_price': unit_price,
                'cost_basis': cost_basis,
                'current_value': current_value,
                'total_cost': total_cost,
                'gain_loss': round(gain_loss, 2),
                'gain_loss_pct': round(gain_loss_pct, 2)
            }

            index_view.append(line)

        # Sort the list of dicts by current_value
        # https://stackoverflow.com/questions/72899/how-can-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary-in-python
        return sorted(index_view, key=lambda x: x["current_value"], reverse=True)

    def get_transaction_history_per_user(self, user_id: int) -> Dict[int, List[Dict[str, Any]]]:
        """
        Query transactions history table to get all records from given userID.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary grouped by symbol_id: {symbol_id: [{row}, {row}, ...], ...}
            Each row contains: transaction_id, user_id, symbol_id, transaction_type,
                             qty, unit_price, cash_after, date (unix timestamp)
        """
        sql = """
            SELECT transaction_id, user_id, symbol_id, transaction_type, qty, unit_price, cash_after,
                   unixepoch(transaction_datetime) AS date
            FROM transactions 
            WHERE user_id = ? 
            ORDER BY transaction_datetime
        """
        result = self.simple_query(sql, (user_id,))
        
        if not isinstance(result, list):
            logger.warning(f"get_transaction_history_per_user: no transactions for user_id={user_id}")
            return {}

        grouped = defaultdict(list)
        for row in result:
            grouped[row.get('symbol_id')].append(row)

        return dict(grouped)

    def _delete_holdings_with_zero_quantity(
        self,
        transaction_history: Dict[int, List[Dict[str, Any]]]
    ) -> Dict[int, List[Dict[str, Any]]]:
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

    def _adjust_for_stock_splits(
        self,
        transaction_history: Dict[int, List[Dict[str, Any]]]
    ) -> Dict[int, List[Dict[str, Any]]]:
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
        query = self.simple_query(sql, tuple(symbol_ids))
        
        if not isinstance(query, list):
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

    def _get_cost_basis(
        self,
        split_adjusted_history: Dict[int, List[Dict[str, Any]]]
    ) -> Dict[int, Dict[str, float]]:
        """
        Calculate cost basis using FIFO accounting method.

        Args:
            split_adjusted_history: Dict of {symbol_id: [split-adjusted transactions]}
                Each transaction should have: transaction_type, qty, unit_price, date

        Returns:
            Dict of {symbol_id: {
                'cost_basis': float,      # Average cost per share (FIFO)
                'total_cost': float       # Total amount paid for remaining shares
            }}

        Note:
            Uses FIFO (First In, First Out) accounting.
            DB Rule: Sales have negative qty

        Example query format:
            SELECT transaction_id, user_id, symbol_id, transaction_type, qty, unit_price,
                   unixepoch(transaction_datetime) AS date
            FROM transactions WHERE user_id = ? ORDER BY transaction_datetime
        """
        cost_basis_data = {}

        for symbol, rows in split_adjusted_history.items():
            # Transaction history is a queue of len(2) lists: [qty, price]
            q = deque()
            
            for row in rows:
                price = row.get('unit_price', 0)
                qty = abs(row.get('qty', 0))
                t_type = row.get('transaction_type', '').lower()

                # If a buy is found, add to the queue
                if t_type == 'buy':
                    q.append([qty, price])

                # If a sell is found, deduct from oldest buys (FIFO)
                elif t_type == 'sell':
                    while qty > 0 and q:
                        if q[0][0] <= qty:
                            # Oldest buy is smaller/equal, remove it entirely
                            qty -= q.popleft()[0]
                        else:
                            # Oldest buy is larger, reduce it
                            q[0][0] -= qty
                            # Break loop
                            qty = 0

                # Unknown transaction type - data integrity issue
                else:
                    logger.error(f"Corrupt transaction row detected symbol: {symbol}, row: {row}")
                    continue

            # When the list of transactions is processed
            # Iterate over the transaction 'objects' and add the total qty, and price
            total_qty = 0.0
            total_price = 0.0
            for transaction in q:
                total_qty += transaction[0]
                total_price += (transaction[1] * transaction[0]) # price * qty

            # Divide price by qty, add to cost_basis dict.
            if total_qty > 0:
                cost_basis_data[symbol] = {
                    'cost_basis': round((total_price / total_qty), 2),
                    'total_cost': round(total_price, 2)
                }
            else:
                cost_basis_data[symbol] = {
                    'cost_basis': 0,
                    'total_cost': 0
                }

        return cost_basis_data