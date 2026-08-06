import datetime
import logging
import os
import time
import uuid
from classes.CommonQueries import CommonQueries
from dotenv import load_dotenv
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException


logger = logging.getLogger(__name__)

class NewsAPIManager(CommonQueries):
    """
    Handles requests to newsAPI. Used to populate the homepage newsfeed alongside news stories
    gathered in '/research'.
    """
    def __init__(self) -> None:
        load_dotenv()
        api_key = os.getenv("NEWS_API_KEY")
        self.api = NewsApiClient(api_key=api_key)

    def response_type_enforce(self, response) -> bool:
        if not isinstance(response, dict):
            logger.error(f"Invalid API response format.")
            return False

        return True

    def handle_return_status(self, response: dict) -> bool:
        """
        Check the "status" field of the APIs return value to see if there's an error.
        """
        status = str(response.get("status")).lower()
        if status == "ok":
            return True
        else:
            logger.error(f"Response status from news API is {status}")
            return False

    def prepare_to_write(self, response: dict) -> list:
        total_results = int(response.get("totalResults", 0))
        if total_results == 0:
            logger.info("Empty api response from newsAPI, but valid return code...")
            return []

        articles = []
        for article in response.get("articles", []):
            if not isinstance(article, dict):
                continue

            def _convert_timestamp():
                datetime_string = article.get("publishedAt")
                if not datetime_string:
                    return None
                try:
                    dt = datetime.datetime.fromisoformat(datetime_string)
                except ValueError:
                    logger.warning(f"Could not parse publishedAt: {datetime_string}")
                    return None
                epoch_float = dt.timestamp()
                epoch_int = int(epoch_float)
                return epoch_int

            articles.append({
                # Not used for dedup on this path (link is, via ON CONFLICT below) - just satisfies the NOT NULL/UNIQUE constraint, since NewsAPI doesn't hand back a stable article id like yahooquery does.
                "uuid": str(uuid.uuid4()),

                "title": article.get("title", "N/A"),
                "thumbnail": article.get("urlToImage"),
                "link": article.get("url"),
                "publisher": (article.get("source") or {}).get("name", "Unknown"),
                "providerPublishTime": _convert_timestamp()
            })

        return articles

    def write_to_db(self, prepared_data: list) -> int:
        """
        Bulk insert articles, skipping any that already exist by link.
        """
        if not prepared_data:
            return 0

        insert_sql = """
        INSERT INTO news
            (uuid, title, thumbnail, link, publisher, providerPublishTime)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(link)
        DO UPDATE SET
        timeInserted=CURRENT_TIMESTAMP, title=excluded.title, thumbnail=excluded.thumbnail,
        publisher=excluded.publisher, providerPublishTime=excluded.providerPublishTime
        """

        rows = [
            (
                item["uuid"],
                item["title"],
                item["thumbnail"],
                item["link"],
                item["publisher"],
                item["providerPublishTime"],
            )
            for item in prepared_data
        ]

        return self.bulk_query(insert_sql, rows, label="news (newsAPI)")

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
            SELECT unixepoch(last_news_api_headlines_fetch) AS last_news_api_headlines_fetch
            FROM global_events
            WHERE id = 1
            """
            try:
                rows = self.select_query(ttl_sql, ())
            except Exception as e:
                logger.exception(e)
            res = None

            if isinstance(rows, list):
                res = rows[0]
            else:
                raise TypeError

            if isinstance(res, dict):
                cache_age = res.get("last_news_api_headlines_fetch")
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
            SET last_news_api_headlines_fetch = ?
            WHERE id = 1
            """
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
            try:
                self.modify_query(stamp_sql, (now, ))
                return True
            except Exception as e:
                logger.exception(e)
                return False

        cache_fresh = _check_ttl()
        if cache_fresh:
            return True

        res = self.api.get_top_headlines(category=category)
        if not self.response_type_enforce(res):
            return False
        if not self.handle_return_status(res):
            return False

        prepared_data = self.prepare_to_write(res)
        self.write_to_db(prepared_data)
        _write_fetch_time()

        return True

    def search_articles(self, query: str, limit: int = 10):
        """
        Call newsAPI's /everything endpoint for the given query, parse response, record to DB.

        Returns the prepared article list, or False on API/response failure.
        """
        safe_query = str(query).strip()
        if not safe_query:
            return False

        try:
            res = self.api.get_everything(q=safe_query, page_size=limit)
        except NewsAPIException as e:
            logger.error(f"newsAPI search failed for '{safe_query}': {e.get_message()}")
            return False

        if not self.response_type_enforce(res):
            return False
        if not self.handle_return_status(res):
            return False

        prepared_data = self.prepare_to_write(res)
        self.write_to_db(prepared_data)

        return prepared_data
