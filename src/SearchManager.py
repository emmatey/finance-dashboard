from APIDataIO import APIDataIO
from CommonQueries import CommonQueries
from ReportManager import ReportManager
from YahooQueryService import YahooQueryService
from datetime import datetime, timedelta
import helpers
import logging

logger = logging.getLogger(__name__)

class SearchManager(CommonQueries):
    """
    Handles searching.
    Can find users, companies, and news stories.
    """
    def search_companies_local(self, query: str, limit=20):
        """
        Return the companies that are close to or the same as what the user is typing.
        Used for "datalist" to give suggestions when user is searching.
        Cards in search page will be filled by yq.search()
        """
        # Convert user input to string and add 'LIKE' wildcards.
        safe_query = f"%{str(query).strip()}%"

        sql = f"""
        SELECT s.ticker, s.company_name, s.quote_type, s.exchange, cp.sector, cp.industry
        FROM symbols AS s
        LEFT JOIN company_profile AS cp
        ON s.id = cp.symbol_id
        WHERE s.ticker LIKE ?
        OR s.company_name LIKE ?
        LIMIT ?
        """
        rows = self.select_query(sql, tuple([safe_query, safe_query, limit]))

        if rows:
            return rows
        else:
            logger.info(f"No data found for {query}")
            return []

    def search_companies_online(self, query: str="", limit:int=20, yq_search_payload: dict={}):
        """
        Search yahooquery for data related to search term.
        
        Args:
            Company Name | 'ticker' : str
            limit: qty of items to return
            yq_search_payload: raw result of calling YahooQuery.Search()
                this paramater exists to allow "search_companies_online" and "search_news" to both extract data
                from the same API call, improving speed and reducing API strain/rate limiting.

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
        res_raw = {}
        if not yq_search_payload:
            res_raw = yqs.yq_search(safe_query, quotes_count=limit, news_count=0)
        else:
            res_raw = yq_search_payload
        
        # Handle API failure
        if not res_raw:  # None from circuit breaker
            logger.warning(f"Yahoo search failed for '{safe_query}' - API may be down")
            return []
        
        # Insert news data which is also pulled from this same API call.
        # Sort of weird but it's already here so why not. A product of yahooquery's design.
        news = res_raw.get("news")
        if news:
            io = APIDataIO()
            processed_news = yqs.extract_news(res_raw)
            io.set_news(processed_news)

        # Extract relevant data.
        out = []
        # Used to filter out tickers listed on multiple exchanges e.g. mmm.de vs mmm
        ticker_bases = set()
        res = res_raw.get('quotes')
        if isinstance(res, list) and all(isinstance(i, dict) for i in res):
            for row in res:
                ticker = row.get('symbol')
                if ticker:
                    split = ticker.split(".")
                    base = split[0]
                    if base in ticker_bases and len(split) > 1:
                        logger.info(f"Company variant detected: {base}. Skipping {ticker}")
                        continue
                    else:
                        ticker_bases.add(base)
                company_name = row.get('longname')
                if not company_name:
                    company_name = row.get('shortname')
                quote_type = row.get("quoteType")
                if quote_type in ['FUTURE', 'CURRENCY', 'OPTION']:
                    continue
                exchange = row.get('exchDisp')
                exchange_short = row.get('exchange')
                if exchange_short in ['PNK', 'OTC']:
                    continue
                sector = row.get('sectorDisp')
                if not sector:
                    sector = row.get('sector', "N/A")
                industry = row.get("industryDisp")
                if not industry:
                    industry = row.get('industry', "N/A")
                
                out.append({
                    "ticker": ticker,
                    "company_name": company_name,
                    "quote_type": quote_type,
                    "exchange": exchange or exchange_short,
                    "sector": sector,
                    "industry": industry,
                })

        else:
            logger.info(f"No data found for {query} in yahoofinance.")

        # Return as list of dicts.
        return out
    
    def search_companies(self, query:str="", limit:int=20, local:bool=False, yq_search_payload: dict={}):
        """
        Search for companies in the DB or online depending on the "local" flag.
        """
        res = None
        query = query.strip()

        if local is True:
            res = self.search_companies_local(query=query, limit=limit)
        else:
            res = self.search_companies_online(query=query, limit=limit, yq_search_payload=yq_search_payload)

        if res is None:
            return []
        else:
            return res
        
    def search_news(self, query: str="", limit: int = 10, yq_search_payload: dict={}) -> list:
        """
        Extract from db the most recent news stories associated with search term up to limit stories.
        Because of limited metadata, this will just be based on article title.
        """
        io = APIDataIO()
        yqs = YahooQueryService()

        # Update the news in DB based on search term
        safe_query = str(query).strip()
        search_result_raw = yqs.yq_search(query=safe_query)

        # Check for yqs_search() payload parameter. Call API if not provided.
        search_result_raw = {}
        if not yq_search_payload:
            search_result_raw = yqs.yq_search(safe_query, quotes_count=limit, news_count=0)
        else:
            search_result_raw = yq_search_payload
        
        # Check if news stories exist, extract and insert them if so
        count = 0
        if isinstance(search_result_raw, dict):
            count = int(search_result_raw.get('count', 0))
            # count shows total items between companies(i.e. 'quotes') and news stories in search() payload
            count = count - len(search_result_raw.get('quotes', 0))
            if count > 0:
                filtered_news = yqs.extract_news(search_result_raw)
                io.set_news(filtered_news)
                return filtered_news
        
        return []

    def search_users(self, query: str, report_manager_instance=None):
        """
        Finds users in database.

        Args:
            query: username to search

        Returns:
            [{
                user_id: int,
                username: str,
                snap_datetime: datetime,
                cash_balance: float,
                portfolio_value: float,
                grand_total: float,
                rank: int
            }]
        """
        if report_manager_instance is None:
            report_manager_instance = ReportManager()

        safe_query = f"%{str(query)}%"
        sql = """
        SELECT id, username
        FROM users
        WHERE username LIKE ?
        """
        rows = self.select_query(sql, tuple([safe_query]))
        if not rows:
            logger.info(f"No results found for {query}")
            return []
        
        user_ids = [row['id'] for row in rows if row.get('id') is not None]

        return report_manager_instance.get_users_ranks(user_ids=user_ids)
