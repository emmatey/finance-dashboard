from DbManager import DbManager


class HomePageYahooQueryService:
    """
    Handles the requesting of data for the home-page from yahoo query
        - Prices of ETFs which represent each continent
        - Price of Gold and Oil etfs
        - Screener for trending stocks
        - Screener for most traded stocks
    """

    # The following tickers will represent each region for the global frontpage market overview.
        # USA = VOO
        # EU Union = VKG
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