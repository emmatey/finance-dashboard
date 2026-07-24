import logging
import time

from APIDataIO import APIDataIO
from CommonQueries import CommonQueries
from enum import Enum
from logging_utils import fmt_data
from MarketOverviewCoordinator import (REGION_OVERVIEW_DISPLAY_NAME_TO_TICKER_MAP)
from StockScreenerManager import StockScreenerManager, TableLifetimes
from YahooQueryService import YahooQueryService

logger = logging.getLogger(__name__)


class UpdateFrequency(Enum):
    """
    Specifies the age at which any given DB table should be updated.
    """

    last_price_update = 5 * 60
    last_snapshot_update = 24 * 60 * 60
    last_screeners_up_to_date = 5 * 60
    last_symbol_cleanup = 24 * 60 * 60

class Daemon(CommonQueries):
    """
    Background task runner for periodic price and balance snapshot updates.

    Runs inside Flask's @app.after_request teardown hook rather than as a
    separate background process. This is intentional: free-tier web hosts don't
    support long-running background processes, so teardown is used to trigger
    updates without requiring one.

    Uses the global_events table to check whether updates are due before running.
    """

    def run(self):
        """
        Runs functions associated with different events in the 'UpdateFrequency'
        table.

        Each updater is responsible for recording its own completion in
        global_events on success, so this loop doesn't need to track
        success/failure itself.
        """
        fresh_report = self.fresh_report()

        # {UpdateFrequency member name: [function(), ...]}
        action_map = {
            'last_price_update': [self.price_updater],
            'last_snapshot_update': [self.balance_snapshot_all_users],
            'last_screeners_up_to_date': [self.update_screener_subset],
            'last_symbol_cleanup': [self.clean_unused_symbols],
        }

        metadata = {
            'actions_performed': [],
        }
        for action, fresh in fresh_report.items():
            if fresh:
                continue
            elif not fresh:
                metadata['actions_performed'].append(action)
            for func in action_map[action]:
                try:
                    func()
                except Exception:
                    logger.exception(f"{action} update failed calling {func.__name__}.")
                    break
            
        if len(metadata["actions_performed"]) == 0:
            logger.info("All daemon tasks up to date. Skipping...")
        else:
            logger.info(f"Daemon Successfully completed {metadata['actions_performed']}")

    def fresh_report(self):
        event_cols = ", ".join(
            f"unixepoch({name}) AS {name}" for name in UpdateFrequency.__members__
        )
        status_sql = f"""
        SELECT {event_cols}
        FROM global_events
        WHERE id = 1
        """
        rows = self.select_query(status_sql, ())
        if not rows or len(rows) != 1:
            logger.critical("Error reading global_events...Skipping updates.")
            return {}
        status = rows[0]
        fresh_report = {task_name : False for task_name in status}

        now = time.time()
        for event_name, age in status.items():
            # age is None when the column has never been stamped - treat as stale.
            if age is None or age < (now - UpdateFrequency[event_name].value):
                fresh_report[event_name] = False
            else:
                fresh_report[event_name] = True
        
        return fresh_report
    
    def update_screener_subset(self, limit=5):
        """
        Updates a portion of the 200+ screeners on every request to share the delay and make it less noticeable.
        The time to fill a screeners request to the yahoo  API grows lineally because the URLs are constructed
        one at a time in a loop, as the endpoint doesn't support lists of tickers.

        Gated by last_screeners_up_to_date in the fresh_report/action_map: once
        a pass finds nothing stale it stamps that column, so run() skips calling
        this again until it's due - otherwise every request would repeat a full
        catalog scan that finds nothing to do.

        That same "nothing stale left" moment is also the one point where the
        whole symbol universe is guaranteed as fresh as it'll get, so the
        derived/custom screeners (volume spikes, volume compression, insider
        surges) are recomputed right there too - see refresh_custom_screeners.
        Previously these ran on their own hourly gate, independent of (and, per
        dict/enum ordering, usually before) this sweep, so they were computing
        against whatever thin, arbitrary slice of the catalog happened to have
        been touched recently rather than a fresh pass over everything.
        """

        sql = f"""
        SELECT
            screener_name,
            (SELECT COUNT(*) FROM screener_ages WHERE unixepoch(last_updated) < ?) as stale_count
        FROM screener_ages
        WHERE unixepoch(last_updated) < ?
        LIMIT {limit}
        """
        age_threshold = int(time.time()) - TableLifetimes.YQ_SCREENER_UPDATE_FREQUENCY.value
        rows = self.select_query(query=sql, placeholders=tuple([age_threshold, age_threshold]))
        screener_names = [row["screener_name"] for row in rows]
        if screener_names:
            logger.info(f"Refreshing {limit} screeners. {rows[0]["stale_count"]} remain stale. ")
            StockScreenerManager().screener_data_update_orchestrator(screener_names=screener_names)
        else:
            # No rows past the age threshold - either everything's fresh or
            # screener_ages is empty (first run). Fall back to a full catalog
            # scan; screener_data_update_orchestrator will no-op on the fresh ones.
            logger.info("No stale rows in screener_ages subset query, falling back to full catalog scan.")
            StockScreenerManager().screener_data_update_orchestrator()
            StockScreenerManager().refresh_custom_screeners()
            self.modify_query(
                "UPDATE global_events SET last_screeners_up_to_date = CURRENT_TIMESTAMP WHERE id = 1",
                (),
            )
            logger.info("Marked last_screeners_up_to_date complete.")

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
            # [{id, val}, {id, val}]
            cash_rows = self.select_query(cash_sql, ())

            # Zip values
            # Goal shape = [(id, cash, holdings), ...]
            snapshot_tuples = []
            for row in cash_rows:
                id = row.get("id")
                if id is None:
                    logger.warning(
                        f"Corrupt row in users table {row}."
                        f"Unable to record balance snapshot."
                    )
                    continue
                cash = row.get("cash", 0)
                portfolio_value = holdings.get(id, 0)

                snapshot_tuples.append((id, cash, portfolio_value))

            # Insert snapshots
            snap_sql = """
                INSERT INTO balance_snapshots
                (user_id, cash_balance, portfolio_value)
                VALUES (?, ?, ?)
            """
            self.bulk_query(snap_sql, snapshot_tuples)

            self.modify_query(
                "UPDATE global_events SET last_snapshot_update = CURRENT_TIMESTAMP WHERE id = 1",
                (),
            )
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
            Uses yq_ticker_fetch_modules() which includes circuit breaker protection.
            Upserts the 'price' module straight into symbols (price, market_state, etc.)
            and also upserts todays_change/todays_change_pct into financial_metrics from
            the same payload, since price_updater already pulls the 'price' module for
            every held ticker every 5 minutes and those fields would otherwise be dropped.
        """
        if yq_service is None:
            yq_service = YahooQueryService()

        try:
            logger.info("Starting price update cycle.")

            # SYMBOLS is a constant from MarketOverviewCoordinator
            placeholders = ", ".join(
                ["?" for _ in REGION_OVERVIEW_DISPLAY_NAME_TO_TICKER_MAP.values()]
            )
            moc_symbols = tuple(
                [s for s in REGION_OVERVIEW_DISPLAY_NAME_TO_TICKER_MAP.values()]
            )
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
            tickers = [row.get("ticker", "") for row in query]

            if not tickers:
                logger.info("No active symbols to update.")
                self.modify_query(
                    "UPDATE global_events SET last_price_update = CURRENT_TIMESTAMP WHERE id = 1",
                    (),
                )
                return True

            # Fetch price modules for all batches using YahooQueryService (with circuit breaker)
            updated_symbols = []
            failed_symbols = []
            change_metrics = {}

            # Call through API gateway with exception handling
            modules_dict = yq_service.yq_ticker_fetch_modules(tickers, ["price"])
            # modules_dict returns None if circuit breaker is active
            if modules_dict is None:
                logger.warning(
                    "Modules fetch returned None - API may be down or circuit breaker active"
                )
                return False
            for symbol, modules in modules_dict.items():
                symbol_safe = str(symbol).strip().upper()
                price_module = modules.get("price")
                if isinstance(price_module, dict):
                    # Successful price retrieval
                    updated_symbols.append(symbol_safe)
                    change_metrics[symbol_safe] = {
                        "todays_change": price_module.get("regularMarketChange"),
                        "todays_change_pct": price_module.get(
                            "regularMarketChangePercent"
                        ),
                    }
                else:
                    # Error message from API or price not available
                    logger.debug(f"Price fetch failed for {symbol}: {price_module}")
                    failed_symbols.append(symbol_safe)

            io = APIDataIO()

            # Upsert price, market_state, exchange, etc. straight into symbols.
            if modules_dict:
                io.upsert_symbols(modules_dict)

            # Upsert same-day change data into financial_metrics.
            # from_screeners=True since this is a partial update (price fields only)
            # and shouldn't mark the rest of the row (PE, dividend yield, etc.) as fresh.
            if change_metrics:
                io.set_financial_metrics(change_metrics, from_screeners=True)

            self.modify_query(
                "UPDATE global_events SET last_price_update = CURRENT_TIMESTAMP WHERE id = 1",
                (),
            )
            logger.info(
                f"Price update complete. Updated: {len(updated_symbols)}, Failed: {len(failed_symbols)}"
            )
            return True

        except Exception:
            logger.exception("price_updater failed")
            return False

    def clean_unused_symbols(self) -> bool:
        """
        Deletes symbols nobody has ever transacted and that aren't a member of
        any currently-tracked screener.

        symbols.id is referenced by financial_metrics, company_profile,
        historical_prices, insider_trades, stock_splits, screener_results,
        fresh_report, and news_symbols, all with ON DELETE CASCADE, so
        deleting the symbol row cleans those up automatically.

        transactions.symbol_id is deliberately NOT cascading - a symbol
        anyone has ever bought or sold can never be deleted this way. The
        WHERE NOT IN clause already excludes those, and the FK constraint
        is the backstop if that filter is ever wrong.

        Returns:
            True on success, False on failure.
        """
        try:
            sql = """
            DELETE FROM symbols
            WHERE id NOT IN (
                SELECT DISTINCT symbol_id FROM transactions WHERE symbol_id IS NOT NULL
            )
            AND id NOT IN (
                SELECT DISTINCT symbol_id FROM screener_results
            )
            """
            deleted = self.modify_query(sql, ())

            self.modify_query(
                "UPDATE global_events SET last_symbol_cleanup = CURRENT_TIMESTAMP WHERE id = 1",
                (),
            )
            logger.info(f"Symbol cleanup removed {deleted} unused symbols.")
            return True

        except Exception:
            logger.exception("clean_unused_symbols failed")
            return False
