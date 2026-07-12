import logging
import time
from APIDataIO import APIDataIO as io
from CommonQueries import CommonQueries
from enum import Enum
from logging_utils import fmt_data
from YahooQueryService import YahooQueryService as yqs

logger = logging.getLogger(__name__)

# Screeners fetched from yahoo query.
YQ_SCREENER_NAMES = [
    "day_gainers",
    "day_losers",
    "most_actives",
    "most_watched_tickers",
    "fifty_two_wk_gainers",
    "fifty_two_wk_losers",
]
# Screeners derived from YQ data
CUSTOM_SCREENERS = ["volume_spike_bullish", "volume_spike_bearish"]


class TableLifetimes(Enum):
    SCREENER_UPDATE_FREQUENCY = 3600  # 1 hour


class StockScreenerManager(CommonQueries):
    """
    Handles fetching, filtering, deriving, and persisting stock screener data
    (yahooquery screeners like 'day_gainers', plus custom screeners derived
    from already-stored data like 'volume_spike_bullish').
    """

    def screener_fresh_report(self, screener_names=YQ_SCREENER_NAMES):
        """
        Checks the age of the screeners to be fetched.
        Returns: [{screener: bool}, ...]
            Fresh = True
            Stale = False
        """
        now = int(time.time())
        update_frequency = TableLifetimes.SCREENER_UPDATE_FREQUENCY.value
        fresh_report = {
            screener_name: False
            for screener_name in screener_names
            if screener_name not in CUSTOM_SCREENERS
        }

        placeholders = ",".join(["?" for _ in screener_names])
        last_updated_sql = f"""
        SELECT screener_name, unixepoch(last_updated) AS last_updated
        FROM screener_ages
        WHERE screener_name IN ({placeholders})
        """
        rows = self.select_query(
            query=last_updated_sql, placeholders=tuple(screener_names)
        )
        for row in rows:
            screener_name = row["screener_name"]
            last_updated = row["last_updated"]
            age = now - int(last_updated)
            if age < update_frequency:
                fresh_report[screener_name] = True
            else:
                fresh_report[screener_name] = False

        return fresh_report

    def fetch_and_filter_screeners(
        self, screener_names, screener_count=100, yqs_instance=None
    ):
        """
        Fetch the given screener names from yahooquery and apply the standard
        quality filters (see YahooQueryService._filter_screener_data).

        Pure fetch+filter - takes a list of any size (one screener for a lazy,
        on-demand refresh; many for a bulk/background sweep) and hands back a
        filtered screeners dict. Callers decide what to do with the result
        (merge in derived/custom screeners, persist it, etc).
        """
        if yqs_instance is None:
            yqs_instance = yqs()

        logger.info(
            f"Fetching {len(screener_names)} screeners: {fmt_data(screener_names)}"
        )
        screeners = yqs_instance.yq_screener_fetch_screeners(
            screeners=screener_names, count=screener_count
        )
        return yqs_instance._filter_screener_data(screeners)

    def write_screener_data(
        self, filtered_screeners, yqs_instance=None, dbio_instance=None
    ):
        """
        Persist an already-filtered screeners dict: extracts metadata/rankings
        and price/financial data, upserts symbols, and writes screener
        rankings + per-screener ages.

        Works for both real (yq-sourced) and derived/custom screener dicts,
        since it only cares about the filtered screener shape, not its origin.
        """
        if yqs_instance is None:
            yqs_instance = yqs()
        if dbio_instance is None:
            dbio_instance = io()

        total_symbols = sum(len(v) for v in filtered_screeners.values())
        logger.info(
            f"Writing screener data: {len(filtered_screeners)} screeners, {total_symbols} symbols"
        )

        # Extract metadata and rankings
        metadata = yqs_instance.extract_screener_metadata(filtered_screeners)

        # Extract price and financial data
        price_modules, financial_metrics = yqs_instance.extract_screener_data(
            filtered_screeners
        )

        # Upsert symbols first (screener rankings reference symbol_id)
        dbio_instance.upsert_symbols(price_modules)

        # Insert screener rankings + refresh their ages (scoped to these screener names)
        dbio_instance.set_screener_results(metadata)
        dbio_instance.set_screener_ages(metadata.keys())

        # Update financial metrics (incomplete data, don't update last_updated timestamp)
        dbio_instance.set_financial_metrics(financial_metrics, from_screeners=True)

    def screener_data_update_orchestrator(
        self,
        yqs_instance=None,
        dbio_instance=None,
    ):
        """
        Checks the age of screener data and updates if stale.
        Updates all screeners if data is older than SCREENER_UPDATE_FREQUENCY.
        """
        if yqs_instance is None:
            yqs_instance = yqs()
        if dbio_instance is None:
            dbio_instance = io()

        fresh_report = self.screener_fresh_report()
        stale_screeners = [
            screener for screener, fresh_bool in fresh_report.items() if not fresh_bool
        ]
        if not stale_screeners:
            logger.info("All screeners up to date, skipping refresh.")
            return

        logger.info(
            f"Screener refresh: {len(stale_screeners)} stale, "
            f"{len(fresh_report) - len(stale_screeners)} fresh."
        )
        filtered_screeners = self.fetch_and_filter_screeners(stale_screeners)

        self.write_screener_data(filtered_screeners, yqs_instance, dbio_instance)
        logger.info("Screener data update orchestrator complete.")

    def volume_spike_screeners(self):
        """
        Find stocks with largest volume spikes, split by price direction.

        Analyzes screener data to identify volume spikes (trading volume significantly
        above 3-month average) and categorizes them as bullish (price up) or bearish
        (price down) based on daily price movement.

        Intended to be run immediately after all yahooquery screeners are updated
        (see screener_data_update_orchestrator), since it reads from financial_metrics
        rows that update populates.
        """

        sql = """
        SELECT s.last_price, s.id, fm.prev_close, fm.todays_volume, fm.three_month_avg_volume
        FROM financial_metrics AS fm
        JOIN symbols AS s
        ON s.id = fm.symbol_id
        WHERE unixepoch(s.last_updated) > ?
        """
        age_threshold = int(time.time()) - int(
            TableLifetimes.SCREENER_UPDATE_FREQUENCY.value
        )
        rows = self.select_query(query=sql, placeholders=tuple([age_threshold]))

        # Calculate relative volume and separate by price direction
        bullish_spikes: list[dict] = []  # Volume spike + price up
        bearish_spikes: list[dict] = []  # Volume spike + price down

        for quote in rows:
            current_vol = quote.get("todays_volume", 0)
            avg_vol_3m = quote.get("three_month_avg_volume", 1)

            # Price change
            current_price = quote.get("last_price", 0)
            prev_close = quote.get("prev_close", 0)

            if (
                avg_vol_3m > 0 and prev_close > 0
            ):  # Prevent divide by 0, crashing with corrupt data
                relative_volume = current_vol / avg_vol_3m
                price_change_pct = ((current_price - prev_close) / prev_close) * 100

                # Only include significant volume spikes (> 1.5x normal)
                if relative_volume > 1.5:
                    spike_data = {
                        "symbol_id": quote.get("id"),
                        "relative_volume": relative_volume,
                    }

                    # Separate by price direction
                    if price_change_pct > 0:
                        bullish_spikes.append(spike_data)
                    else:
                        bearish_spikes.append(spike_data)

        # Sort by relative volume (highest spike first)
        bullish_spikes.sort(key=lambda x: x["relative_volume"], reverse=True)
        bearish_spikes.sort(key=lambda x: x["relative_volume"], reverse=True)

        # Add Rank
        for idx, company in enumerate(bullish_spikes, start=1):
            company["rank"] = idx
            company["screener_name"] = "volume_spike_bullish"
        for idx, company in enumerate(bearish_spikes, start=1):
            company["screener_name"] = "volume_spike_bearish"
            company["rank"] = idx

        # Clear old rows for these two derived screeners before reinserting
        self.modify_query(
            """
            DELETE FROM screener_results
            WHERE screener_name IN (?, ?)
            """,
            tuple(CUSTOM_SCREENERS)
        )

        # Insert into DB
        insert_sql = """
            INSERT INTO screener_results (symbol_id, screener_name, rank)
            VALUES (?, ?, ?)
        """
        screener_tuples = []
        for screener in bullish_spikes + bearish_spikes:
            screener_result = (
                screener["symbol_id"],
                screener["screener_name"],
                screener["rank"],
            )
            screener_tuples.append(screener_result)

        self.bulk_query(query=insert_sql, data_list=screener_tuples, label="screener_results")
