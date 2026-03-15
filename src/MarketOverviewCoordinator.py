import datetime as dt
import logging
from typing import Dict, Optional
from ResearchDataIO import ResearchDataIO as io
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

    def update_region_etfs(self, symbols=SYMBOLS, yqs_instance=yqs(), dbio_instance=io()):
        """
        Update the underlying data for the ETFs in the SYMBOLS dict.
        
        Data required for homepage:
            - Ticker / Symbol
            - Current price
            - Percent change from yesterday's close.
        """
        # call get modules.
        modules = yqs_instance.yq_ticker_get_modules(
            symbols=[s for s in self.SYMBOLS.values()], 
            modules=['price', 'defaultKeyStatistics', 'summaryDetail', 'financialData'])

        # Upsert symbols
        for region, ticker in symbols.items():
            dbio_instance.upsert_symbol(ticker, modules)

        # call get and set financial metrics for all symbols.
        metrics = yqs_instance.get_financial_metrics(modules)
        dbio_instance.set_financial_metrics(metrics)