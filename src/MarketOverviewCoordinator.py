import logging
import time
from APIDataIO import APIDataIO as io
from CommonQueries import CommonQueries
from enum import Enum
from YahooQueryService import YahooQueryService as yqs

logger = logging.getLogger(__name__)

# ETF tickers representing each region for global market overview
SYMBOLS = {
    'USA': 'VOO',
    'EU': 'IEUR',
    'LATAM': 'ILF',
    'Africa': 'AFK',
    'Australia': 'EWA',
    'India': 'INDA',
    'Japan': 'EWJ',
    'China': 'MCHI',
    'Gold': 'GLD',
    'Copper': 'CPER',
    'Oil': 'USO'
}
# Screeners fetched from yahoo query.
YQ_SCREENER_NAMES = [
        'day_gainers', 
        'day_losers', 
        'most_actives', 
        'most_watched_tickers', 
        'fifty_two_wk_gainers', 
        'fifty_two_wk_losers'
    ]
# Screeners derived from YQ data
CUSTOM_SCREENERS = [
    'volume_spike_bullish',
    'volume_spike_bearish'
]

class TableLifetimes(Enum):
    REGION_ETFS_UPDATE_FREQUENCY = 3600 # 1 hour
    SCREENER_UPDATE_FREQUENCY = 3600 # 1 hour

class MarketOverviewCoordinator(CommonQueries):
    """
    Handles updating and retrieving data for the home page market overview.
    """

    def initialize_regional_etfs(self, symbols: dict=SYMBOLS, yqs_instance=None, dbio_instance=None):
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
            logger.info(f"Regional ETFs up to date! age = {age}. Update frequency = {TableLifetimes.REGION_ETFS_UPDATE_FREQUENCY.value}")
            return None

        logger.info(f"Initializing regional ETF data for {len(symbols)} regions")

        modules = yqs_instance.yq_ticker_fetch_modules(
            symbols=tickers,
            modules=['price', 'defaultKeyStatistics', 'summaryDetail', 'financialData']
        )

        dbio_instance.upsert_symbols(modules)
        metrics = yqs_instance.extract_financial_metrics(modules)
        dbio_instance.set_financial_metrics(metrics)

        logger.info(f"Successfully initialized regional ETF data for {', '.join(symbols.keys())}")

    def screener_data_update_orchestrator(self, screener_names=YQ_SCREENER_NAMES, screener_count=100, yqs_instance=None, dbio_instance=None):
        """
        Checks the age of screener data and updates if stale.
        Updates all screeners if data is older than SCREENER_UPDATE_FREQUENCY.

        Note: All screeners will have the same age as the screener metadata table is cleared on each update.
        """
        if yqs_instance is None:
            yqs_instance = yqs()
        if dbio_instance is None:
            dbio_instance = io()
            
        age_sql = """
        SELECT UNIXEPOCH(MIN(last_updated)) AS last_updated
        FROM screener_results
        """
        rows = self.select_query(age_sql, ())
        last_updated = 0
        if rows and isinstance(rows, list) and len(rows) >= 1:
            last_updated = rows[0].get("last_updated") or 0
        
        age = time.time() - last_updated
        if age < TableLifetimes.SCREENER_UPDATE_FREQUENCY.value:
            logger.info(f"Screeners up to date! age = {age}. Update frequency = {TableLifetimes.SCREENER_UPDATE_FREQUENCY.value}")
            return None

        screeners = yqs_instance.yq_screener_fetch_screeners(screeners=screener_names, count=screener_count)
        filtered_screeners = yqs_instance._filter_screener_data(screeners)

        # Add custom volume spike screeners
        relative_volumes_screener = yqs_instance.extract_relative_volumes(filtered_screeners)
        filtered_screeners.update(relative_volumes_screener)

        # Extract metadata and rankings
        metadata = yqs_instance.extract_screener_metadata(filtered_screeners)

        # Extract price and financial data
        price_modules, financial_metrics = yqs_instance.extract_screener_data(filtered_screeners)

        # Upsert symbols first (screener rankings reference symbol_id)
        dbio_instance.upsert_symbols(price_modules)

        # Insert screener rankings (clears table first, so all get same timestamp)
        dbio_instance.set_screeners_metadata(metadata)

        # Update financial metrics (incomplete data, don't update last_updated timestamp)
        dbio_instance.set_financial_metrics(financial_metrics, from_screeners=True)

        logger.info(f"Successfully updated {len(filtered_screeners)} screeners with {len(price_modules)} unique tickers")
        
        return None