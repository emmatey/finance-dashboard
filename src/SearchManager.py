from DbManager import DbManager
from APIDataIO import APIDataIO
from YahooQueryService import YahooQueryService
from datetime import datetime, timedelta
import helpers
import logging
import yahooquery as yq

logger = logging.getLogger(__name__)

class SearchManager(DbManager):
    """
    Handle the search bar.
    Should show a union of db results and yq.search results in a search results page unless user types an exact match.
    In which case user should be directed right to the page in question.
    """
    def search_companies_local(self, query: str):
        """
        Return the companies that are close to or the same as what the user is typing.
        """
        # Convert user input to string and add 'LIKE' wildcards.
        safe_query = f"%{str(query)}%"

        sql = """
        SELECT *
        FROM symbols 
        WHERE ticker LIKE ?
        OR company_name LIKE ?
        LIMIT 15
        """
        rows = self.simple_query(sql, tuple([safe_query, safe_query]))

        if rows:
            return rows
        else:
            logger.info(f"No data found for {query}")
            return None

    def search_companies_online(self, query: str):
        """
        Check if symbol exists online using YahooQueryService.
        """
        # Convert query to string.
        safe_query: str = str(query)

        # Search with yahoo query search() method.
        res_raw = yq.search(safe_query, quotes_count=10, news_count=0)
        
        # Extract relevant data.
        out = []
        res = res_raw.get('quotes')
            # checks res is a list of dicts.
        if isinstance(res, list) and all(isinstance(i, dict) for i in res):
            for row in res:
                quote_type = row.get("quoteType")
                if quote_type in ['FUTURE', 'CURRENCY', 'OPTION']:
                    continue
                
                ticker = row.get('symbol')
                name = row.get('longname')
                if not name:
                    name = row.get('shortname')

                if ticker and name:
                    out.append({
                        'quote_type': quote_type,
                        'ticker': ticker,
                        'company_name': name
                    })
        else:
            logger.info(f"No data found for {query} in yahoofinance.")

        # Return as list of dicts.
        return out

    def online_offline_union(self, online_results, offline_results):
        """
        Compares online and offline results from user query. Meaning API and DB.
        Returns a dataset which eliminates dubplicate results.
        """
        pass