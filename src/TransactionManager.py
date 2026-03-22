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


    def record_buy_order_in_transactions_table(self, ):
        """
        Query db to record a buy after prior verification.

        """

    def write_pending_transaction_to_session(self, session, tx_type: str):
        """

        """
        pass

    ## Buy route ##
    # Verify symbol exists - Done
        # if exists but not in db, call insert funciton. DONE
    # Calculate purchase price - Can be done in route
        #
    # Check user can afford - Can be done with balance func (exists) - purchase price calculated
    # Record order in session token with age

    # Redirect to confirmation screen!
        # Render transaction data
        # Fetch new price from DB (updated by daemnon every 60 seconds globally)
        # System to fetch updated data

    # Recirect to confirm route
        # fetch new price from DB
        # Write to transactions -
        # balance snapshot
        # redirect home
