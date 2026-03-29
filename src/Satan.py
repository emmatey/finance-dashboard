from app import app
import logging

from CommonQueries import CommonQueries
from enum import Enum
from MarketOverviewCoordinator import MarketOverviewCoordinator as moc
from time import time
from YahooQueryService import YahooQueryService



logger = logging.getLogger(__name__)

class TableLifetimes(Enum):
    """
    Specifies the age at which any given DB table should be updated.
    Done on a per-table basis because the 'research_api_helpers' are written to fetch and organize
    the data required to populate one record in one DB table each.
    """
    price = 60  # symbols table
    balance_snapshot = 86400  # 24 hours
    regional_markets = 3600 # 1 hour
    screeners = 3600 # 1 hour

class Satan(CommonQueries):
    """
    The deamon manager (please laugh). 
    Will be run in a separate process to app.py.
    Currently will not really be 'daemons' but just a script that does these two operations and then dies.
    """
      
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
        Update all stock prices using YahooQueryService.
        Designed to be called once per execution by threading.Timer or scheduler.
        Thread loop and timing should be managed in app.py.

        Args:
            yq_service: Instance of YahooQueryService for API calls.
                        Instantiates a new instance if not provided.

        Returns:
            True on success, False on failure.
            Returns False early if circuit breaker is active.

        Note:
            Fetches prices in batches of 200 to avoid API limits.
            Uses yq_ticker_fetch_price_map() which includes circuit breaker protection.
        """
        if yq_service is None:
            yq_service = YahooQueryService()
            
        try:
            logger.info("Starting price update cycle.")

            # Query DB for all active symbols
            query = self.select_query("SELECT ticker FROM symbols", ())
            tickers = [row.get('ticker') for row in query]

            if not tickers:
                logger.info("No active symbols to update.")
                return True

            # Break into batches of 200
            batch_size = 200
            batches = []
            buffer = []
            for t in tickers:
                if len(buffer) < batch_size:
                    buffer.append(t)
                else:
                    batches.append(buffer)
                    buffer = []
                    buffer.append(t)
            if buffer:
                batches.append(buffer)

            # Fetch prices for all batches using YahooQueryService (with circuit breaker)
            updated_symbols = []
            failed_symbols = []

            for batch in batches:
                # Call through API gateway with exception handling
                price_map = yq_service.yq_ticker_fetch_price_map(batch)

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

updaters = {
    'last_price_update': Satan.price_updater,
    'last_screener_update': moc.screener_data_update_orchestrator,
    'last_regional_update': moc.initialize_regional_etfs,
    'last_snapshot_update': Satan.balance_snapshot_all_users,
}

if __name__ == "__main__":
    with app.app_context():
        satan = Satan()

        fresh_sql = """
        SELECT
            last_price_update AS price             
            last_snapshot_update AS snap
            last_regional_etfs_update AS region
            last_screener_data_update AS screen
        FROM global_events
        WHERE id = 1
        """
        row = satan.select_query(fresh_sql, ())

        
       