import datetime as dt
import logging
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
    SCREENER_UPDATE_FREQUENCY = 3600 # One Hour

    def initialize_regional_etfs(self, symbols=SYMBOLS, yqs_instance=yqs(), dbio_instance=io()):
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
        modules = yqs_instance.yq_ticker_fetch_modules(
            symbols=tickers,
            modules=['price', 'defaultKeyStatistics', 'summaryDetail', 'financialData']
        )
        
        # Upsert symbols (ticker, company_name, last_price)
        dbio_instance.upsert_symbols(modules)
        
        # Extract and store financial metrics (includes prev_close for pct_change calculation)
        metrics = yqs_instance.extract_financial_metrics(modules)
        dbio_instance.set_financial_metrics(metrics)
        
        logger.info(f"Successfully initialized regional ETF data for {', '.join(symbols.keys())}")

    def screener_data_update_orchestrator(self, screener_names=YQ_SCREENER_NAMES, screener_count=100, yqs_instance=yqs(), dbio_instance=io()):
        """
        Checks the age of screener data and updates if stale.
        Updates all screeners if data is older than SCREENER_UPDATE_FREQUENCY.
        """
        # Check freshness of screener data
        sql = """
            SELECT MIN(unixepoch(last_updated)) as oldest_update
            FROM screener_results
        """
        res = self.simple_query(sql, ())

        if not isinstance(res, list) or not res:
            logger.info("No screener data found - performing initial load")
            needs_update = True
        else:
            oldest_update = res[0].get('oldest_update')

            if oldest_update is None:
                logger.info("No screener data found - performing initial load")
                needs_update = True
            else:
                # Compare age against threshold
                now = dt.datetime.now(dt.timezone.utc)
                last_update = dt.datetime.fromtimestamp(oldest_update, dt.timezone.utc)
                age = (now - last_update).total_seconds()

                if age > self.SCREENER_UPDATE_FREQUENCY:
                    logger.info(f"Screener data is {age:.0f}s old (threshold: {self.SCREENER_UPDATE_FREQUENCY}s) - updating")
                    needs_update = True
                else:
                    logger.info(f"Screener data is fresh ({age:.0f}s old) - skipping update")
                    needs_update = False

        if not needs_update:
            return

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
