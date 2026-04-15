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
        Search yahooquery for data related to search term.
        
        Args:
            Company Name | 'ticker' : str

        Returns:
        [{
            ticker: str,
            company_name: str,
            quote_type: str,
            exchange: str,
            sector: str,
            industry: str,
        }, ...  ]

        """
        yqs = YahooQueryService()

        # Convert query to string.
        safe_query: str = str(query).strip()

        # Search with yahoo query search() method.
        res_raw = yqs.yq_search(safe_query, quotes_count=20, news_count=0)
        
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
                ticker = row.get('symbol')
                company_name = row.get('longcompany_name')
                if not company_name:
                    company_name = row.get('shortname')
                quote_type = row.get("quoteType")
                if quote_type in ['FUTURE', 'CURRENCY', 'OPTION']:
                    continue
                exchange = row.get('exchange')
                if exchange in ['PNK', 'OTC']:
                    continue
                sector = row.get('sectorDisp')
                if not sector:
                    sector = row.get('sector', "N/A")
                industry = row.get("industryDisp")
                if not industry:
                    industry = row.get('industry', "N/A")
                
                out.append({
                    ticker: ticker,
                    company_name: company_name,
                    quote_type: quote_type,
                    exchange: exchange,
                    sector: sector,
                    industry: industry,
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