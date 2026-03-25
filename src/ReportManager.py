import logging
import math
from CommonQueries import CommonQueries
from collections import defaultdict, deque
from typing import Dict, List, Union, Any


logger = logging.getLogger(__name__)

class ReportManager(CommonQueries):
    """
    Handles displaying information about user. I.e holdings, transaction history, account balance/grand total

    Read from DB, format for frontend.
    """

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
        raw_history = self.get_transaction_history(user_id)
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
        query_raw = self.select_query(sql, tuple(stock_ids))
        
        if not query_raw:
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

    def get_transaction_history(self, user_id: int = 0, all_users: bool = False) -> dict[int, list[dict]]:
        """
        Query transaction history, grouped by symbol_id.
    
        Args:
            user_id: The user's ID. Required if all_users is False.
            all_users: If True, fetch transactions for all users.
    
        Returns:
            Dict of {symbol_id: [transactions]} where each transaction contains:
            transaction_id, user_id, symbol_id, transaction_type,
            qty, unit_price, cash_after, date (unix timestamp)
    
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
        
        return grouped
    
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

    def get_balance_snapshot_history(self, user_id: int):
        """
        Retrieves the balance snapshot data history for a given user.
        Used to power the account value history graph.
        """
        pass

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
    