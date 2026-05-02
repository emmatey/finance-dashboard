import logging
import time

from CommonQueries import CommonQueries
from enum import Enum
from MarketOverviewCoordinator import MarketOverviewCoordinator, SYMBOLS
from YahooQueryService import YahooQueryService



logger = logging.getLogger(__name__)

class UpdateFrequency(Enum):
    """
    Specifies the age at which any given DB table should be updated.
    """
    price = 300 # symbols table
    balance_snapshot = 86400  # 24 hours

class Satan(CommonQueries):
    """
    The deamon manager (please laugh). 
    Will be run in a separate process to app.py.
    Currently will not really be 'daemons' but just a script that does these two operations and then dies.
    """
    def run(self):
        """
        Decide which functions to call. 
        Write to db as complete immidately to block parallel requests from performing the same actions,
        revert to NULL on exception.
        Update again on success to reflect true completion time.
        """
        status_sql = """
        SELECT 
            unixepoch(last_price_update) AS price,
            unixepoch(last_snapshot_update) AS snap
        FROM global_events
        WHERE id = 1
        """
        logger.debug("Satan is running...")
        status = self.select_query(status_sql, ())
        if not status or len(status) != 1:
            logger.critical(f"Error reading global_events...Skipping updates.")
            return
        
        to_update = []
        to_update_funcs = []
        price_time = status[0].get("price")
        if not price_time:
            price_time = 0
        if time.time() - price_time > UpdateFrequency.price.value:
            to_update.append("last_price_update")
            to_update_funcs.append(self.price_updater)
        snap_time =  status[0].get("snap")
        if not snap_time:
            snap_time = 0
        if time.time() - snap_time > UpdateFrequency.balance_snapshot.value:
            to_update.append("last_snapshot_update")
            to_update_funcs.append(self.balance_snapshot_all_users)
        if not to_update:
            logger.debug("All satan tables up to date, skipping...")
            return
        
        update_placeholders = ", ".join(f"{i} = ?" for i in to_update)
        update_sql = f"""
        UPDATE global_events
        SET {update_placeholders}
        WHERE id = 1
        """

        utc_now = time.gmtime() 
        params = [time.strftime('%Y-%m-%d %H:%M:%S', utc_now) for _ in to_update]
        
        self.modify_query(update_sql, tuple(params))
        for func in to_update_funcs:
            ret = func()
            if ret is False:
                revert_sql = f"UPDATE global_events SET {', '.join(f'{col} = NULL' for col in to_update)} WHERE id = 1"
                self.modify_query(revert_sql, ())
        utc_now = time.gmtime() 

        params = [time.strftime('%Y-%m-%d %H:%M:%S', utc_now) for _ in to_update]
        self.modify_query(update_sql, tuple(params))

    def balance_snapshot_all_users(self) -> bool:
        """
        Create balance snapshots for ALL users.

        Returns:
            True on success, False on failure
        """
        try:
            # {id: val, id: val}
            holdings = self.get_all_users_holdings_values()
            
            # Get cash balance
            cash_sql = """
            SELECT id, cash
            FROM users
            """
            #[{id, val}, {id, val}]
            cash_rows = self.select_query(cash_sql, ())

            # Zip values
            # Goal shape = [(id, cash, holdings), ...]
            snapshot_tuples = []
            for row in cash_rows:
                id = row.get('id')
                if id is None:
                    logger.warning(
                        f"Corrupt row in users table {row}."
                        f"Unable to record balance snapshot.")
                    continue
                cash = row.get('cash', 0)
                portfolio_value = holdings.get(id, 0)

                snapshot_tuples.append((id, cash, portfolio_value))

            # Insert snapshots
            snap_sql = """
                INSERT INTO balance_snapshots
                (user_id, cash_balance, portfolio_value)
                VALUES (?, ?, ?)
            """
            self.bulk_query(snap_sql, snapshot_tuples)

            logger.info("All user snapshots completed successfully.")
            return True

        except Exception:
            logger.exception("balance_snapshot_all_users failed")
            return False

    def price_updater(self, yq_service=None) -> bool:
        """
        Update all stock prices.

        Args:
            yq_service: Instance of YahooQueryService for API calls.
                        Instantiates a new instance if not provided.

        Returns:
            True on success, False on failure.
            Returns False early if circuit breaker is active.

        Note:
            Uses yq_ticker_fetch_price_map() which includes circuit breaker protection.
        """
        if yq_service is None:
            yq_service = YahooQueryService()
            
        try:
            logger.info("Starting price update cycle.")

            # SYMBOLS is a constant from MarketOverviewCoordinator
            placeholders = ", ".join(["?"for _ in SYMBOLS.values()])
            moc_symbols = tuple([s for s in SYMBOLS.values()])
            # Query DB for all active symbols
            tickers_query = f"""
            SELECT DISTINCT s.ticker
            FROM symbols s
            WHERE s.id IN (
                SELECT symbol_id 
                FROM transactions
                GROUP BY symbol_id
                HAVING SUM(qty) > 0
            )
            OR s.ticker IN ({placeholders})
            """
            # Checks for tickers users currently own and regional indicator ETFs
            # Reduces time yahooquery takes as checking 1000+ tickers takes over 50 seconds
            # A good place to update later, the source of price data in specific.
            query = self.select_query(tickers_query, moc_symbols)
            tickers = [row.get('ticker', "") for row in query]

            if not tickers:
                logger.info("No active symbols to update.")
                return True

            # Fetch prices for all batches using YahooQueryService (with circuit breaker)
            updated_symbols = []
            failed_symbols = []

            # Call through API gateway with exception handling
            price_map = yq_service.yq_ticker_fetch_price_map(tickers)
            # price_map returns None if circuit breaker is active
            if price_map is None:
                logger.warning("Price map returned None - API may be down or circuit breaker active")
                return False
            for symbol, price in price_map.items():
                symbol_safe = str(symbol).strip().upper()
                if isinstance(price, float):
                    # Successful price retrieval
                    updated_symbols.append((price, symbol_safe))
                elif isinstance(price, str):
                    # Error message from API
                    logger.debug(f"Price fetch failed for {symbol}: {price}")
                    failed_symbols.append((symbol_safe,))
                elif price is None:
                    # Price not available in response
                    logger.debug(f"Price not available for {symbol}")
                    failed_symbols.append((symbol_safe,))

            # Update symbols table with new prices
            if updated_symbols:
                update_sql = """
                UPDATE symbols
                SET last_price = ?, last_updated = CURRENT_TIMESTAMP
                WHERE ticker = ?
                """
                self.bulk_query(update_sql, updated_symbols)

            logger.info(f"Price update complete. Updated: {len(updated_symbols)}, Failed: {len(failed_symbols)}")
            return True

        except Exception:
            logger.exception("price_updater failed")
            return False