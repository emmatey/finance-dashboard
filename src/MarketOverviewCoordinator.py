import datetime as dt
from DbManager import DbManager


class MarketOverviewCoordinator(DbManager):
    """
    This class will be uesd to handle updating and retrieving all the data used on the home-page / market overview.
    Curently this includes
        - World markets ETFs - Current price and % change vs last close
        - Oil, Gold & Copper ETFs - Current price and % change vs last close
        - Most traded stocks today - From screeners
        - Trending stocks - From screeners

    """

    # The following tickers will represent each region for the global frontpage market overview.
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

    # Query for last day updated for all stocks.
    # If stock not updated today for any
    # Check if market is open
        # If no, return
    # call modules for get financial metrics and upsert symbol
    # call methods to extract required data
    # call dbio to insert
    # query to return (ticker, price, last market close)
    # calculate change 
    # return region: data as dicts
    def update_regional_overview(self):
        """
        """
        symbols = list(self.SYMBOLS.values())
        placeholders = ", ".join(['?' for _ in symbols])

        sql = f"""
        SELECT s.ticker, fm.last_updated
        FROM symbols as s
        JOIN financial_metrics as fm
        ON s.id = fm.symbol_id
        WHERE s.ticker IN ({placeholders})
        """
        # Select last updated time of financial_metrics for each symbol
        rows = self.simple_query(sql, tuple(symbols))
        assert isinstance(rows, list) 

        # add all companies not found in initial query to 'needs update' list
        needs_update = [s for s in symbols if s not in [i.get('ticker') for i in rows]]

        # Check which symbols haven't been updated today already.
        today = dt.date.today()
        for row in rows: # type: ignore
            if isinstance(row, dict):
                ticker = row.get('ticker', '')
                last_updated_str = row.get('last_updated', "1970-1-2 12:13:14")
                last_updated_date = dt.datetime.strptime(last_updated_str, "%Y-%m-%d %H:%M:%S").date()
                 
                if not last_updated_date == today:
                    needs_update.append(ticker)
        
        
        

