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

    def get_global_market_overview(self):
        """
        Call this method if market is open and last update of financial metrics wasn't today.
        """
        # This method will be used to pull the prices and % change from last close for the ETFs which will represent each region.
        # We need prev close and price
        # Prev close can be handled by calling 
        # yqs get financial metrics > data io set financial 
        # Price will be handled by update daemon but need to initially upsert.
        # upsert symbol and get financial metrics both need price moduel

        # 0. Query for last update of all ETFs last close price, use oldest.
        # 1. call get modules method. 
        # 2. call upsert symbol
        # 3. call yqs financial metrics
        # 4. call data in for metrics
        # 5. get price and compare to prev close. calculate % difference 