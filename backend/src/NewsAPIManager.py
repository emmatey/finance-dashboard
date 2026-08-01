import datetime
import logging
import os
import time
from CommonQueries import CommonQueries
from dotenv import load_dotenv
from newsapi import NewsApiClient


logger = logging.getLogger(__name__)

class NewsAPIManager(CommonQueries):
    """
    Handles requests to newsAPI. Used to populate the homepage newsfeed alongside news stories
    gatherd in '/research'.
    """
    def __init__(self) -> None:
        load_dotenv()
        api_key = os.getenv("NEWS_API_KEY")

        self.api = NewsApiClient(api_key=api_key)
    
    def fetch_and_cache_headlines(self, category="business", cache_ttl=(60*60*1)):
        """
        Call newsAPI, parse response, record to DB.
        """
        def _check_ttl():
            fresh = False

            ttl_sql = """
            SELECT last_global_headlines_fetch
            FROM global_events
            WHERE id = 1
            """
            res = self.select_query(ttl_sql, ())
            if isinstance(res, dict):
                date_time = res.get("last_global_headlines_fetch")
                if not date_time:
                    return fresh
                else:
                    current_time_utc_seconds = time.time()
                    last_updated_utc_seconds = 
                
            else:
                logger.error("global_events table query, not returning a dict as usual, check live db schema.")
                return fresh

            return fresh
        
        def _write_fetch_time():
            pass

        def _handle_return_status():
            pass

        def _prepate_to_write():
            pass

        def _write_to_db():
            pass

        _check_ttl()

