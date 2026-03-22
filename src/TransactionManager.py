from DbManager import DbManager
from APIDataIO import APIDataIO
from YahooQueryService import YahooQueryService
from datetime import datetime, timedelta
import helpers
import logging


logger = logging.getLogger(__name__)


class TransactionManager(DbManager):
    """
    Handles Buy/Sell, Deposit/Withdraw, and supporting methods.

    Data flow:
        Fetch current price > show user their current holdings of the given stock as well as price data >
        on confirm fetch price agian > write tx to database

        Note: Price update daemon will be updating all holding prices in the background, no need to manually do this here.
    Attributes:
        yq_service: YahooQueryService instance for API interactions
    """

    def __init__(self, yq_service=YahooQueryService()):
        """
        Initialize TransactionManager with Yahoo Query Service.

        Args:
            yq_service: Instance of YahooQueryService for fetching stock data
        """
        self.yq_service = yq_service


    def record_transacton(self, ):
        """
        

        """
        pass

    def get_pricing_info(self):
        """

        """

    def check_can_afford(self, user_id, ticker, qty) -> bool:
        """
        """
        pass

    


    # What this needs to be
        # Record buy/sell to transactions table
        # Get info about user holdings of the relevant stock for the confirmation screen


