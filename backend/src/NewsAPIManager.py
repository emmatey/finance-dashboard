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
            """
            If True, fresh.
            """
            fresh = False

            ttl_sql = """
            SELECT unixepoch(last_global_headlines_fetch) AS last_global_headlines_fetch
            FROM global_events
            WHERE id = 1
            """
            rows = self.select_query(ttl_sql, ())
            res = None

            if isinstance(rows, list):
                res = rows[0]
            else:
                raise TypeError
            
            if isinstance(res, dict):
                cache_age = res.get("last_global_headlines_fetch")
                if not cache_age:
                    return fresh
                else:
                    current_time_utc_seconds = int(time.time())
                    if (cache_age + cache_ttl) > current_time_utc_seconds:
                        fresh = True
            else:
                raise TypeError

            return fresh
        
        def _write_fetch_time():
            """
            Must write in utc time.
            """
            stamp_sql = """
            UPDATE global_events
            SET last_global_headlines_fetch = ?
            WHERE id = 1
            """
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
            try:
                self.modify_query(stamp_sql, (now, ))
                return True
            except:
                return False

        def _handle_return_status():
            pass

        def _prepare_to_write():
            pass

        def _write_to_db():
            pass

        _write_fetch_time()

