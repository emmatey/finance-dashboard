from DbManager import DbManager
from functools import wraps
from requests.exceptions import ConnectionError, Timeout, HTTPError
from time import sleep, time
from typing import Tuple

import logging


logger = logging.getLogger(__name__)

class YahooAPIClient(DbManager):
    """
    Wrapper for yahooquery API calls with error handling.
    All Yahoo API calls should go through this class.
    """
    def __init__(self):
        logger.info("Initializing YahooAPIClient...")

    def api_status(self) -> tuple[bool, bool]:
        """
        If api is set to 'DOWN' handle exponential backoff.
        Returns: (is_up, should_retry)
        """
        query = """
        SELECT yq_api_status,
            unixepoch(yq_api_down_at) as down_at,
            yq_api_retries as retries
        FROM global_events
        """
        result = self.select_query(query, ())
        print(result)
        assert isinstance(result, list)
        if not result:
            logger.error("global_events row missing")
            return (False, False)
        api_status = result[0]

        if api_status.get("yq_api_status", "DOWN") == "UP":
            return (True, True)

        down_at = api_status.get("down_at", 0)
        retries = api_status.get("retries", 0)

        # Apply backoff formula to see if retry is warranted
        base_delay = 300  # 5 minutes
        max_delay = 3600  # 1 hour
        current_wait = min(base_delay * (2 ** retries), max_delay)
        time_since_last_try = time() - down_at

        # Log if too early
        if time_since_last_try < current_wait:
            logger.debug(
                f"Retry too early, skipping attempt, retry will be available in {current_wait - time_since_last_try} seconds.")
            return (False, False)

        elif time_since_last_try >= current_wait:
            return (False, True)
        
        else:
            # Please stop yelling at me language server
            return (False, False)

    def set_api_down(self):
        """
        Set API status to down and timestamp.
        """
        query = """
        UPDATE global_events
        SET yq_api_status = 'DOWN',
        yq_api_down_at = CURRENT_TIMESTAMP,
        yq_api_retries = 0
        """
        self.modify_query(query, ())

    def set_api_up(self):
        """
        Set API status to up and clear timestamp/retry count.
        """
        query = """
        UPDATE global_events
        SET yq_api_status = 'UP', yq_api_down_at = NULL, yq_api_retries = 0
        """
        self.modify_query(query, ())

    def api_increment_retries(self):
        """
        Increment API retries counter
        """
        query = """
        UPDATE global_events
        SET yq_api_retries = yq_api_retries + 1
        """
        self.modify_query(query, ())

    def api_downcrement(self, api_up: bool, func, attempts, args):
        """
        Down + Increment (please laugh)
        """
        if api_up is True:
            self.set_api_down()
            logger.error(f"{func.__name__} failed after {attempts} attempts for args={args}")
        else:
            self.api_increment_retries()
            logger.info(f"Incremented global API retry counter after. {func.__name__} was called.")


yq_client = YahooAPIClient()

def yq_exception_handler(client_instance=yq_client):
    """
    Catches and logs exceptions.
    Sets api status to 'UP' on sucesses.
    Retries 3 times for connection error or timeout exceptions.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Abort early if API is marked 'DOWN' and retry has been too recent.
            api_up, api_should_retry = client_instance.api_status()
            if api_up is False and api_should_retry is False:
                logger.debug(f"{func.__name__} skipped - API down, backoff active")
                return None

            attempts = 3
            for attempt in range(1, attempts + 1):
                try:
                    logger.info(f"Attempting {func.__name__} (Attempt {attempt} of {attempts})")
                    res = func(*args, **kwargs)
                    if api_up is False:
                        client_instance.set_api_up()
                    return res

                except (ConnectionError, Timeout) as e:
                    logger.warning(f"Network error (attempt {attempt}/{attempts}): {e}")
                    if attempt < attempts:
                        sleep(2 * attempt)
                        continue
                    else:
                        client_instance.api_downcrement(api_up, func, attempts, args)
                        return None

                except HTTPError as e:
                    code = e.response.status_code
                    if code == 429:
                        logger.critical("429: Rate limited by Yahoo. Backing off.")
                        client_instance.api_downcrement(api_up, func, attempts, args)
                        return None
                    elif code == 404:
                        logger.error(f"404: Ticker not found. Args: {args}")
                        return None

                    # Try again for other HTTP errors
                    if attempt < attempts:
                        sleep(2 * attempt)
                        continue
                    else:
                        logger.error(f"HTTP Error {code}: {e}")
                        client_instance.api_downcrement(api_up, func, attempts, args)

                except Exception as e:
                    logger.error(f"Unexpected error in YahooQuery: {str(e)}")
                    raise

            return None
        return wrapper
    return decorator
