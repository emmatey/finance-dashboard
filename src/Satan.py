import logging

from DbManager import DbManager
from enum import Enum
from ReportManager import ReportManager



logger = logging.getLogger(__name__)

class TableLifetimes(Enum):
    """
    Specifies the age at which any given DB table should be updated.
    Done on a per-table basis because the 'research_api_helpers' are written to fetch and organize
    the data required to populate one record in one DB table each.
    """
    price = 60  # symbols table
    balance_snapshot = 86400  # 24 hours


class Satan(DbManager):
    """
    The deamon manager (please laugh). Will be run in a separate process to app.py
    """

    def balance_snapshot_all_users(self) -> bool:
        """
        Create balance snapshots for ALL users.

        Designed to be called once per execution by threading.Timer or scheduler.
        Thread loop and timing should be managed in app.py.

        Returns:
            True on success, False on failure
        """
        try:
            rm = ReportManager()

            # Query all cash
            cash_sql = "SELECT id, cash FROM users"
            cash_query = self.select_query(cash_sql, ())
            cash_map = {row.get('id'): row.get('cash') for row in cash_query}

            # Calculate holdings value
            holdings_value_per_user = rm.get_all_holdings_values()

            # Zip values
            grand_total_per_user = []
            for user in cash_map:
                # [(user_id, cash_balance, portfolio_value)]
                grand_total_per_user.append((
                    user,
                    cash_map[user],
                    holdings_value_per_user.get(user, 0)
                ))
                logger.info(f"Snapshot created for User: {user}!")
                logger.info(f"Balance: {cash_map[user]} Holdings: {holdings_value_per_user.get(user, 0)}.")

            # Insert snapshots
            sql = """
                INSERT INTO balance_snapshots
                (user_id, cash_balance, portfolio_value)
                VALUES (?, ?, ?)
            """
            self.bulk_query(sql, grand_total_per_user)

            logger.info("All user snapshots completed successfully.")
            return True

        except Exception:
            logger.exception("balance_snapshot_all_users failed")
            return False

    def price_updater(self, yq_service) -> bool:
        """
        Update all stock prices using YahooQueryService.

        Designed to be called once per execution by threading.Timer or scheduler.
        Thread loop and timing should be managed in app.py.

        Args:
            yq_service: Instance of YahooQueryService for API calls

        Returns:
            True on success, False on failure

        Note:

            Fetches prices in batches of 200 to avoid API limits.
            Uses yq_ticker_price_map() which includes circuit breaker protection.
            Marks symbols as inactive if price fetch fails.
        """
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
                price_map = yq_service.yq_ticker_price_map(batch)

                # price_map returns None if circuit breaker is active
                if price_map is None:
                    logger.warning("Price map returned None - API may be down or circuit breaker active")
                    continue

                for symbol, price in price_map.items():
                    if isinstance(price, float):
                        # Successful price retrieval
                        updated_symbols.append((price, symbol.upper()))
                    elif isinstance(price, str):
                        # Error message from API
                        logger.debug(f"Price fetch failed for {symbol}: {price}")
                        failed_symbols.append((symbol.upper(),))
                    elif price is None:
                        # Price not available in response
                        logger.debug(f"Price not available for {symbol}")
                        failed_symbols.append((symbol.upper(),))

            # Update symbols table with new prices
            if updated_symbols:
                self.bulk_query(
                    "UPDATE symbols SET last_price = ?, last_updated = CURRENT_TIMESTAMP WHERE ticker = ?",
                    updated_symbols
                )

            logger.info(f"Price update complete. Updated: {len(updated_symbols)}, Failed: {len(failed_symbols)}")
            return True

        except Exception:
            logger.exception("price_updater failed")
            return False
