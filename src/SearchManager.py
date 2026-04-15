from CommonQueries import CommonQueries
from YahooQueryService import YahooQueryService
from datetime import datetime, timedelta
import helpers
import logging

logger = logging.getLogger(__name__)

class SearchManager(CommonQueries):
    """
    Handle the search bar.
    Should show a union of db results and yq.search results.
    """
    def search_companies_local(self, query: str, limit=15):
        """
        Return the companies that are close to or the same as what the user is typing.
        """
        # Convert user input to string and add 'LIKE' wildcards.
        safe_query = f"%{str(query)}%"

        sql = f"""
        SELECT *
        FROM symbols 
        WHERE ticker LIKE ?
        OR company_name LIKE ?
        LIMIT ?
        """
        rows = self.select_query(sql, tuple([safe_query, safe_query, limit]))

        if rows:
            return rows
        else:
            logger.info(f"No data found for {query}")
            return None

    def search_companies_online(self, query: str):
        """
        Check if symbol exists online using YahooQueryService.
        """
        yqs = YahooQueryService()

        # Convert query to string.
        safe_query: str = str(query).strip()

        # Search with yahoo query search() method.
        res_raw = yqs.yq_search(safe_query, quotes_count=10, news_count=0)
        
        # Handle API failure
        if not res_raw:  # None from circuit breaker
            logger.warning(f"Yahoo search failed for '{safe_query}' - API may be down")
            return []
        
        # Extract relevant data.
        out = []
        res = res_raw.get('quotes')
            # checks res is a list of dicts.
        if isinstance(res, list) and all(isinstance(i, dict) for i in res):
            for row in res:
                quote_type = row.get("quoteType")
                if quote_type in ['FUTURE', 'CURRENCY', 'OPTION', 'INDEX']:
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

    def online_offline_union(self, offline_results, online_results):
        """
        Compares online and offline results from user query. Meaning API and DB.
        Returns a dataset which eliminates duplicate results.
        """
        results = offline_results + online_results
        
        seen = set()
        unique_results = []
        for res in results:
            ticker = res.get('ticker')
            if ticker and ticker not in seen:
                seen.add(ticker)
                unique_results.append(res)

        return unique_results