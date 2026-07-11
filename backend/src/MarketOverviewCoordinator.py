import logging
import time
from APIDataIO import APIDataIO as io
from CommonQueries import CommonQueries
from enum import Enum
from YahooQueryService import YahooQueryService as yqs

logger = logging.getLogger(__name__)

# ETF tickers representing each region for global market overview
REGION_OVERVIEW_DISPLAY_NAME_TO_TICKER_MAP = {
    "USA S&P 500": "VOO",
    "USA Dow": "DIA",
    "USA Nasdaq": "QQQ",
    "USA Russell 2000": "IWM",
    "EU": "IEUR",
    "LATAM": "ILF",
    "Africa": "AFK",
    "Australia": "EWA",
    "India": "INDA",
    "Japan": "EWJ",
    "China": "MCHI",
    "Gold": "GC=F",
    "Copper": "HG=F",
    "Oil": "CL=F",
}
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
CUSTOM_SCREENERS = [
    "volume_spike_bullish", 
    "volume_spike_bearish"
]
ALL_SCREENERS = CUSTOM_SCREENERS + YQ_SCREENER_NAMES


class TableLifetimes(Enum):
    REGION_ETFS_UPDATE_FREQUENCY = 3600  # 1 hour
    SCREENER_UPDATE_FREQUENCY = 3600  # 1 hour


class MarketOverviewCoordinator(CommonQueries):
    """
    Handles updating and retrieving data for the home page market overview.
    """

    def initialize_regional_etfs(
        self,
        symbols: dict = REGION_OVERVIEW_DISPLAY_NAME_TO_TICKER_MAP,
        yqs_instance=None,
        dbio_instance=None,
    ):
        """
        Initialize or refresh regional ETF data for homepage market overview display.
        Checks freshness before updating — skips if data is newer than REGION_ETFS_UPDATE_FREQUENCY.

        Example:
            >>> coordinator = MarketOverviewCoordinator()
            >>> coordinator.initialize_regional_etfs()
            >>> regional_data = dbio.get_regional_overview(coordinator.SYMBOLS)
        """
        if yqs_instance is None:
            yqs_instance = yqs()
        if dbio_instance is None:
            dbio_instance = io()

        # Check freshness using MIN(last_updated) on regional ETF tickers
        tickers = list(symbols.values())
        placeholders = ", ".join("?" for _ in tickers)
        age_sql = f"""
        SELECT UNIXEPOCH(MIN(fm.last_updated)) AS last_updated
        FROM financial_metrics fm
        JOIN symbols s ON s.id = fm.symbol_id
        WHERE s.ticker IN ({placeholders})
        """
        rows = self.select_query(age_sql, tuple(tickers))
        last_updated = 0
        if rows and isinstance(rows, list) and len(rows) >= 1:
            last_updated = rows[0].get("last_updated") or 0

        age = time.time() - last_updated
        if age < TableLifetimes.REGION_ETFS_UPDATE_FREQUENCY.value:
            logger.info(
                f"Regional ETFs up to date! age = {age}. Update frequency = {TableLifetimes.REGION_ETFS_UPDATE_FREQUENCY.value}"
            )
            return None

        logger.info(f"Initializing regional ETF data for {len(symbols)} regions")

        modules = yqs_instance.yq_ticker_fetch_modules(
            symbols=tickers,
            modules=["price", "defaultKeyStatistics", "summaryDetail", "financialData"],
        )

        dbio_instance.upsert_symbols(modules)
        metrics = yqs_instance.extract_financial_metrics(modules)
        dbio_instance.set_financial_metrics(metrics)

        logger.info(
            f"Successfully initialized regional ETF data for {', '.join(symbols.keys())}"
        )

    def screener_fresh_report(self, screener_names=ALL_SCREENERS):
        """
        Checks the age of the screeners to be fetched.
        Returns: [{screener: bool}, ...]
            Fresh = True
            Stale = False
        """
        now = int(time.time())
        update_frequency = TableLifetimes.SCREENER_UPDATE_FREQUENCY.value
        fresh_report = {screener_name: False for screener_name in screener_names}

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

        # Extract metadata and rankings
        metadata = yqs_instance.extract_screener_metadata(filtered_screeners)

        # Extract price and financial data
        price_modules, financial_metrics = yqs_instance.extract_screener_data(
            filtered_screeners
        )

        # Upsert symbols first (screener rankings reference symbol_id)
        dbio_instance.upsert_symbols(price_modules)

        # Insert screener rankings + refresh their ages (scoped to these screener names)
        dbio_instance.set_screeners_metadata(metadata)

        # Update financial metrics (incomplete data, don't update last_updated timestamp)
        dbio_instance.set_financial_metrics(financial_metrics, from_screeners=True)

    def screener_data_update_orchestrator(
        self,
        screener_names=YQ_SCREENER_NAMES,
        screener_count=100,
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
            screener_name
            for screener_name, fresh_bool in fresh_report.items()
            if not fresh_bool
        ]

    

        self.write_screener_data(filtered_screeners, yqs_instance, dbio_instance)

        logger.info(
            f"Successfully updated {len(filtered_screeners)} screeners with {len(price_modules)} unique tickers"
        )

        return None
