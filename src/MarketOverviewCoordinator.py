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
    
    Currently includes:
        - World markets ETFs - Current price and % change vs last close
        - Oil, Gold & Copper ETFs - Current price and % change vs last close
        - Most traded stocks today - From screeners
        - Trending stocks - From screeners
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

    def initialize_regional_etfs(self, symbols=None, yqs_instance=None, dbio_instance=None):
        """
        Initialize or refresh regional ETF data for homepage market overview display.
        
        Fetches and stores comprehensive data for regional market ETFs (VOO, IEUR, etc.)
        that represent major global markets. This method ensures all necessary data
        exists in the database for get_regional_overview() to display current market
        performance.
        
        Workflow:
            1. Fetch comprehensive modules from Yahoo Finance API (price, statistics, etc.)
            2. Upsert symbol records (ticker, company_name, last_price)
            3. Extract and store financial metrics (prev_close, market_cap, etc.)
            4. Data is then available for get_regional_overview() to calculate pct_change
        
        Args:
            symbols: Dict mapping region names to ETF tickers
                    Default: self.SYMBOLS = {'USA': 'VOO', 'Europe': 'IEUR', ...}
            yqs_instance: YahooQueryService instance for API calls
                         Default: instantiates new instance
            dbio_instance: APIDataIO instance for database operations
                          Default: instantiates new instance
        
        Database Tables Updated:
            - symbols: ticker, company_name, last_price, last_updated
            - financial_metrics: prev_close, market_cap, beta, etc.
        
        Companion Method:
            get_regional_overview() - Queries stored data to calculate and display
                                     regional market performance with percent changes
        
        Note:
            - This should be called periodically (e.g., daily market open) to refresh data
            - get_regional_overview() relies on this data being fresh (checks last_updated)
            - Fetches complete metrics (not from screeners) so last_updated IS updated
        
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
        
        # Fetch comprehensive module data from Yahoo Finance
        tickers = list(symbols.values())
        modules = yqs_instance.yq_ticker_get_modules(
            symbols=tickers,
            modules=['price', 'defaultKeyStatistics', 'summaryDetail', 'financialData']
        )
        
        # Upsert symbols (ticker, company_name, last_price)
        for region, ticker in symbols.items():
            dbio_instance.upsert_symbol(ticker, modules)
        
        # Extract and store financial metrics (includes prev_close for pct_change calculation)
        metrics = yqs_instance.get_financial_metrics(modules)
        dbio_instance.set_financial_metrics(metrics)  # from_screeners=False (default)
        
        logger.info(f"Successfully initialized regional ETF data for {', '.join(symbols.keys())}")