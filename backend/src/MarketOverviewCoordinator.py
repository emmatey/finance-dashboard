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

class TableLifetimes(Enum):
    REGION_ETFS_UPDATE_FREQUENCY = 3600  # 1 hour


class MarketOverviewCoordinator(CommonQueries):
    """
    Handles updating and retrieving data for the home page market overview:
    regional/US market index ETFs and commodities.
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
