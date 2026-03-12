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

    def update_regional_overview(
        self, 
        yqs_instance: Optional[yqs] = yqs(), 
        db_io_instance: Optional[io] = io()
    ) -> Dict[str, Dict[str, float]]:
        """
        Refresh data for ETFs representing regional markets.
        
        Args:
            yqs_instance: YahooQueryService instance (creates new if None)
            db_io_instance: ResearchDataIO instance (creates new if None)
        
        Returns:
            Dict mapping region names to market data:
            {
                'USA': {
                    'ticker': 'VOO',
                    'current_price': 614.16,
                    'prev_close': 622.03,
                    'pct_change': -1.27,
                    'last_updated': '2026-03-12 19:25:21'
                },
                ...
            }
        """
        if not yqs_instance or not db_io_instance:
            raise ValueError("Method requires YahooQueryService and ResearchDataIO instances.")
        
        symbols = list(self.SYMBOLS.values())
        placeholders = ", ".join(['?' for _ in symbols])
        
        # Check which symbols need updating
        sql = f"""
            SELECT s.ticker, fm.last_updated
            FROM symbols as s
            JOIN financial_metrics as fm
            ON s.id = fm.symbol_id
            WHERE s.ticker IN ({placeholders})
        """
        
        rows = self.simple_query(sql, tuple(symbols))
        assert isinstance(rows, list)
        
        # Add symbols not found in DB to 'needs update' list
        needs_update = [s for s in symbols if s not in [i.get('ticker') for i in rows]]
        
        # Check which symbols haven't been updated today
        today = dt.date.today()
        for row in rows:
            ticker = row.get('ticker', '')
            if not ticker:
                continue
                
            last_updated_str = row.get('last_updated', "1970-01-02 12:13:14")
            try:
                last_updated_date = dt.datetime.strptime(
                    last_updated_str, "%Y-%m-%d %H:%M:%S"
                ).date()
            except ValueError:
                logger.warning(f"Invalid date format for {ticker}: {last_updated_str}")
                needs_update.append(ticker)
                continue
            
            if last_updated_date != today:
                needs_update.append(ticker)
        
        # If nothing needs updating, return current data
        if not needs_update:
            logger.info("All regional ETFs already updated today. Returning cached data.")
            return self.get_regional_overview()
        
        # Fetch fresh data from Yahoo API
        logger.info(f"Updating {len(needs_update)} regional ETFs: {needs_update}")
        modules = yqs_instance.yq_ticker_get_modules(
            needs_update, 
            ['price', 'defaultKeyStatistics', 'summaryDetail', 'financialData']
        )
        
        if not modules:
            logger.error("Failed to fetch modules from Yahoo API")
            return self.get_regional_overview()  # Return stale data rather than failing
        
        # Upsert symbols (price, company name)
        for symbol in needs_update:
            db_io_instance.upsert_symbol(symbol, modules)
        
        # Upsert financial metrics (includes prev_close)
        metrics = yqs_instance.get_financial_metrics(modules)
        db_io_instance.set_financial_metrics(metrics)
        
        logger.info(f"Successfully updated {len(needs_update)} ETFs")
        
        # Return fresh data
        return self.get_regional_overview()

    def get_regional_overview(self) -> Dict[str, Dict[str, float]]:
        """
        Retrieve current regional market data from database.
        
        Returns:
            Dict mapping region names to market data:
            {
                'USA': {
                    'ticker': 'VOO',
                    'current_price': 614.16,
                    'prev_close': 622.03,
                    'pct_change': -1.27,
                    'last_updated': '2026-03-12 19:25:21'
                },
                ...
            }
        """
        symbols = list(self.SYMBOLS.values())
        placeholders = ", ".join(['?' for _ in symbols])
        
        sql = f"""
            SELECT 
                s.ticker,
                s.last_price as current_price,
                fm.prev_close,
                fm.last_updated,
                ((s.last_price - fm.prev_close) / fm.prev_close * 100) as pct_change
            FROM symbols s
            JOIN financial_metrics fm ON s.id = fm.symbol_id
            WHERE s.ticker IN ({placeholders})
        """
        
        rows = self.simple_query(sql, tuple(symbols))
        assert isinstance(rows, list)
        
        # Map ticker symbols back to region names
        ticker_to_region = {v: k for k, v in self.SYMBOLS.items()}
        
        result = {}
        for row in rows:
            ticker = row.get('ticker', '')
            if not ticker:
                continue
                
            region = ticker_to_region.get(ticker, ticker)
            
            result[region] = {
                'ticker': ticker,
                'current_price': row.get('current_price'),
                'prev_close': row.get('prev_close'),
                'pct_change': round(row.get('pct_change', 0), 2),
                'last_updated': row.get('last_updated')
            }
        
        logger.debug(f"Retrieved market data for {len(result)} regions")
        return result