import datetime as dt
import logging
from typing import Dict, Optional
from APIDataIO import APIDataIO as io
from YahooQueryService import YahooQueryService as yqs
from DbManager import DbManager

logger = logging.getLogger(__name__)


class MarketOverviewCoordinator(DbManager):
    """
    Handles updating and retrieving data for the home page market overview.
    """

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

    SCREENER_UPDATE_FREQUENCY = 3600 # One Hour

    def initialize_regional_etfs(self, symbols=None, yqs_instance=None, dbio_instance=None):
        """
        Initialize or refresh regional ETF data for homepage market overview display.
        
        Fetches and stores comprehensive data for regional market ETFs (VOO, IEUR, etc.)
        that represent major global markets. This method ensures all necessary data
        exists in the database for get_regional_overview() to display current market
        performance.
        
        Method checks if 'financial_metrics' have been updated today, and skips API calls if so.
    
        Example:
            >>> coordinator = MarketOverviewCoordinator()
            >>> # Initialize/refresh ETF data
            >>> coordinator.initialize_regional_etfs()
            >>> 
            >>> # Later, homepage can retrieve formatted data
            >>> regional_data = dbio.get_regional_overview(coordinator.SYMBOLS)
            >>> # Returns: {'USA': {'ticker': 'VOO', 'current_price': 614.16,
            >>> #                    'prev_close': 622.03, 'pct_change': -1.27}, ...}
        """
        # Use defaults if not provided
        if symbols is None:
            symbols = self.SYMBOLS
        if yqs_instance is None:
            yqs_instance = yqs()
        if dbio_instance is None:
            dbio_instance = io()

        logger.info(f"Initializing regional ETF data for {len(symbols)} regions")
        
        # Check if prev_close (via financial metrics) has been updated today already.
        placeholders = ",".join(["?" for _ in symbols.values()])
        sql = f"""
        SELECT fm.last_updated 
        FROM financial_metrics AS fm
        JOIN symbols AS s ON s.id = fm.symbol_id
        WHERE s.ticker IN ({placeholders})
        """
        res = self.simple_query(sql, tuple(symbols.values()))
        assert isinstance(res, list)

        oldest = dt.datetime.max.replace(tzinfo=dt.timezone.utc)
        tickers_found = 0
        for row in res:
            time = row.get('last_updated')
            if isinstance(time, str):
                tickers_found += 1
                last_updated = dt.datetime.strptime(time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
                
                if last_updated < oldest:
                    oldest = last_updated

            else:
                logger.warning(f"Date-Time string {time} from {row} malformed, skipping. Should be str is {type(time)}.")

        if oldest.date() == dt.date.today() and tickers_found == len(symbols.values()):
            logger.info(f"All regional representative tickers present and updated today.")
            return

        # Fetch comprehensive module data from Yahoo Finance
        tickers = list(symbols.values())
        modules = yqs_instance.yq_ticker_get_modules(
            symbols=tickers,
            modules=['price', 'defaultKeyStatistics', 'summaryDetail', 'financialData']
        )
        
        # Upsert symbols (ticker, company_name, last_price)
        dbio_instance.upsert_symbols(modules)
        
        # Extract and store financial metrics (includes prev_close for pct_change calculation)
        metrics = yqs_instance.get_financial_metrics(modules)
        dbio_instance.set_financial_metrics(metrics)
        
        logger.info(f"Successfully initialized regional ETF data for {', '.join(symbols.keys())}")

    def screener_data_update_orchestrator(self, yqs_instance=yqs(), dbio_instance=io()):
        """
        Checks the age of all screeners.
        Updates them all if any are older than the "SCREENER_UPDATE_FREQUENCY".
        """
        # Select all screeners and look for oldest update time.

        # Fetch screener data, filter, and add custom screener.
        screener_names = ['day_gainers', 'day_losers', 'most_actives', 'most_watched_tickers', 'fifty_two_wk_gainers', 'fifty_two_wk_losers']
        screeners = yqs_instance.yq_screener_get_screeners(screeners=screener_names, count=100)
        filtered_screeners = yqs_instance._filter_screener_data(screeners)
        relative_volumes_screener = yqs_instance.get_relative_volumes(filtered_screeners)
        filtered_screeners.update(relative_volumes_screener)
        
        # Extract metadata and add to db
        metadata = yqs_instance.get_screener_metadata(filtered_screeners)
        dbio_instance.set_screeners_metadata(metadata)

        # Extract data and add to db
        price_module, financial_metrics_module = yqs_instance.get_screener_data(filtered_screeners)
        dbio_instance.upsert_symbols(price_module)
        dbio_instance.set_financial_metrics(financial_metrics_module)