from DbManager import DbManager


class MarketOverviewCoordinator:
    """
    This class will be uesd to handle updating and retrieving all the data used on the home-page / market overview.
    Curently this includes
        - - User rank among active players.
        - World markets ETFs - Current price and % change vs last close
        - Oil, Gold & Copper ETFs - Current price and % change vs last close
        - Most traded stocks today - From screeners
        - Trending stocks - From screeners

    """

    # The following tickers will represent each region for the global frontpage market overview.
        # USA = VOO
        # EU Union = ieur
        # LATAM = ILF
        # Africa = AFK
        # AUS = EWA
        # India = INDA
        # Japan = EWJ
        # China = MCHI

        # Gold = GLD
        # Copper = CPER
        # Oil = USO

        # Use price module and price dict method to get both prev close, and their current prices.

    # Use Screener module to get trending stocks, biggest movers, and highest volume

    


    symbols = ['voo','ieur','ilf','afk','ewa','inda','ewj','mchi','gld','cper','uso']


