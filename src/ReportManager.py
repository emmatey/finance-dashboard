import datetime
import logging
from CommonQueries import CommonQueries
from collections import deque, defaultdict
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
        adjusted_history = self.tx_history_company_grouped(user_id)
        cost_basis_data = self._get_cost_basis(adjusted_history)

        # Query db for all stocks at once to avoid the so called 'N+1 queries' problem.
        # https://planetscale.com/blog/what-is-n-1-query-problem-and-how-to-solve-it
        stock_ids = list(adjusted_history.keys())
        if not stock_ids:
            logger.debug(f"No portfolio holdings for user_id={user_id}")
            return []
        
        placeholders = ', '.join(['?' for _ in stock_ids])
        sql = f"SELECT id, ticker, company_name, last_price FROM symbols WHERE id IN ({placeholders})"
        try:
            query_raw = self.select_query(sql, tuple(stock_ids))
        except Exception:
            raise
            
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

    def get_balance_snapshot_history(self, user_id: int) -> list[dict]:
        """
        Retrieves the balance snapshot data history for a given user.
        Used to power the account value history graph.

        Returns 
        {   
            username: str
            snap_datetime: datetime,
            cash_balance: float,
            portfolio_value: float,
            grand_total: float
        }
        """

        sql = """
        SELECT 
            u.username,
            ss.snap_datetime, 
            ss.cash_balance,
            ss.portfolio_value,
            ss.grand_total
        FROM balance_snapshots AS ss
        JOIN users AS u
        ON u.id = ss.user_id
        WHERE user_id = ?
        """
        return self.select_query(sql, (user_id, ))

    def get_transaction_history(self, user_id: int) -> list[dict]:
        """
        Returns the transaction history of a given user.

        Args:
            user_id

        Returns:
            [{tx}, {tx}, ...]

            tx = {
            'transaction_id': int,
            'user_id': int,
            'symbol_id': int, 
            'transaction_type': str,
            'qty': int,
            'unit_price': int,
            'cash_after': float,
            'transaction_datetime': datetime
            }
        """
        sql = """
        SELECT * 
        FROM transactions
        WHERE user_id = ?
        ORDER BY transaction_datetime DESC
        """
        return self.select_query(sql, (user_id, ))

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
    
    def calculate_insider_sentiment(self, ticker: str, modules: dict, timeframe_in_months: int = 5) -> float:
        """
        Find the ratio of insider buys to sells of the company's own security. Used as a measure of sentiment. 
        Weights buys 5x sales because backtesting research says this is a stronger signal.
            Source: my ass, trust me bro

        Args:
            insider_tx_module -
                result of get_modules with insiderTransactions as one of the parameters
                https://yahooquery.dpguthrie.com/guide/ticker/modules/#insider_transactions
                Shape = TICKER: {insiderTransactions: {transactions:[{
                    ...
                    startDate: datetime.date,
                    shares: int,
                    transactionText: str,
                    ...
                    }, {}, ...
                ]}}
            ticker - Company stock ticker.
            timeframe_in_months - Cutoff time in months of the oldest tx used.

        Returns:
            float
        
        Raises:
            ValueError - if insiderTrades module isnt found or ticker provided isn't found
        """
        buy_str = "Purchase at price"
        sell_str = "Sale at price"
        ticker = str(ticker).upper().strip()

        N_MONTHS = datetime.timedelta(days=(30 * timeframe_in_months))
        today = datetime.datetime.today()
        n_months_ago = today - N_MONTHS

        # 'i' is the tickers in the modules dict
        found = False
        for i in modules:
            if str(i).upper().strip() != ticker:
                continue
            else:
                found = True
        if found is False:
            no_ticker_found_err = f"ticker {ticker} not found in insider_tx_module module dict."
            logger.error(no_ticker_found_err)
            raise ValueError(no_ticker_found_err)
        
        raw_modules = modules[ticker]
        found = False
        for module in raw_modules:
            if module != "insiderTransactions":
                continue
            else:
                found = True
        if found is False:
            module_missing_err = "Insider transactions module missing from modules parameter."
            logger.error(module_missing_err)
            raise ValueError(module_missing_err)
        
        insider_tx_module = raw_modules["insiderTransactions"]
        tx_list = insider_tx_module["transactions"]
        buy_volume = 0
        sell_volume = 0
        for tx in tx_list:
            try:
                tx_date = datetime.datetime.strptime(tx.get('startDate', "1970-01-01"), "%Y-%m-%d")
            except (ValueError, TypeError):
                continue
            # Skip transaction if older than 5 yrs
            if tx_date < n_months_ago:
                continue

            tx_text = tx.get("transactionText", "")
            if buy_str in tx_text:
                buy_volume += tx.get("shares")
            elif sell_str in tx_text:
                sell_volume += tx.get("shares")
            
        logger.debug(f"Raw buy volume for {ticker} is: {buy_volume}")
        logger.debug(f"Raw sell volume for {ticker} is: {sell_volume}")

        


        



    def get_all_users_ranks(self) -> list[dict]:
        """Get rank for all users"""
        sql = """
            WITH latest_snapshots AS (
                SELECT *
                FROM balance_snapshots
                JOIN users ON users.id = balance_snapshots.user_id
                WHERE snap_id IN (
                    SELECT MAX(snap_id)
                    FROM balance_snapshots
                    GROUP BY user_id
                )
            ),
            ranked AS (
                SELECT username, user_id, snap_datetime, portfolio_value,
                cash_balance, grand_total,
                RANK() OVER (ORDER BY grand_total DESC) AS rank
                FROM latest_snapshots
            )
            SELECT * FROM ranked 
        """
        return self.select_query(sql, ())

    def get_users_ranks(self, user_ids: list[int]) -> list[dict]:
        """
        Get rank for specific users
        returns {
            username,
            user_id,
            snap_datetime,(datetime of the source of the balnace figures)
            portfolio_value,
            cash_balance,
            grand_total,
            rank
            }
        """
        if not user_ids:
            return []
        if not all(isinstance(i, int) for i in user_ids):
            raise TypeError("user_ids must contain only integers")

        placeholders = ", ".join("?" * len(user_ids))
        sql = f"""
            WITH latest_snapshots AS (
                SELECT *
                FROM balance_snapshots
                JOIN users ON users.id = balance_snapshots.user_id
                WHERE snap_id IN (
                    SELECT MAX(snap_id)
                    FROM balance_snapshots
                    GROUP BY user_id
                )
            ),
            ranked AS (
                SELECT username, user_id, snap_datetime, portfolio_value,
                    cash_balance, grand_total,
                    RANK() OVER (ORDER BY grand_total DESC) AS rank
                FROM latest_snapshots
            )
            SELECT * FROM ranked 
            WHERE user_id IN ({placeholders})
        """
        return self.select_query(sql, tuple(user_ids))