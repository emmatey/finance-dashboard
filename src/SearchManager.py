from APIDataIO import APIDataIO
from CommonQueries import CommonQueries
from ReportManager import ReportManager
from YahooQueryService import YahooQueryService
import logging

logger = logging.getLogger(__name__)


class SearchManager(CommonQueries):
    """
    Handles searching across companies, users, and news stories.
    """

    def search_companies_local(self, query: str, limit: int = 20) -> list[dict]:
        """
        Search the local database for companies matching the query.
        Used for datalist suggestions on each keystroke — fast, no API call.

        Args:
            query: Partial ticker or company name to search for
            limit: Maximum number of results to return (default: 20)

        Returns:
            List of dicts with keys: ticker, company_name, quote_type, exchange, sector, industry
            Returns empty list if no results found.
        """
        safe_query = f"%{str(query).strip()}%"
        sql = """
        SELECT s.ticker, s.company_name, s.quote_type, s.exchange, cp.sector, cp.industry
        FROM symbols AS s
        LEFT JOIN company_profile AS cp ON s.id = cp.symbol_id
        WHERE s.ticker LIKE ?
        OR s.company_name LIKE ?
        LIMIT ?
        """
        rows = self.select_query(sql, (safe_query, safe_query, limit))
        if rows:
            return rows
        logger.info(f"No local results found for '{query}'")
        return []

    def search_companies_online(
        self,
        query: str = "",
        limit: int = 20,
        yq_search_payload: dict | None = None
    ) -> list[dict]:
        """
        Search Yahoo Finance for companies matching the query.
        
        If yq_search_payload is provided, extracts company data from it directly
        instead of making a new API call. This allows the /search route to reuse
        a single yq.search() response for both companies and news.

        Note:
            If the payload contains news stories, they are extracted and inserted
            into the local database as a side effect.

        Args:
            query: Company name or ticker to search for
            limit: Maximum number of results to return (default: 20)
            yq_search_payload: Optional raw yq.search() response to extract from.
                               If not provided, a new API call will be made.

        Returns:
            List of dicts with keys: ticker, company_name, quote_type, exchange, sector, industry
            Returns empty list on API failure or no results.
        """
        yqs = YahooQueryService()

        if yq_search_payload is None:
            safe_query = str(query).strip()
            yq_search_payload = yqs.yq_search(safe_query, quotes_count=limit, news_count=10)

        if not yq_search_payload:
            logger.warning(f"Yahoo search failed for '{query}' - API may be down")
            return []

        # News comes free from the same API call — extract and cache it
        if yq_search_payload.get("news"):
            io = APIDataIO()
            processed_news = yqs.extract_news(yq_search_payload)
            io.set_news(processed_news)

        # Extract company quotes
        out = []
        ticker_bases = set()  # tracks base tickers to filter exchange variants e.g. MMM.DE
        quotes = yq_search_payload.get('quotes', [])

        if not isinstance(quotes, list) or not all(isinstance(i, dict) for i in quotes):
            logger.info(f"No company results found for '{query}' in Yahoo Finance.")
            return []

        for row in quotes:
            ticker = row.get('symbol')
            if not ticker:
                continue

            # Skip exchange variants of already-seen tickers
            parts = ticker.split(".")
            base = parts[0]
            if base in ticker_bases and len(parts) > 1:
                logger.info(f"Skipping exchange variant: {ticker}")
                continue
            ticker_bases.add(base)

            # Filter unwanted quote types
            quote_type = row.get("quoteType")
            if quote_type in ['FUTURE', 'CURRENCY', 'OPTION']:
                continue

            # Filter OTC/Pink Sheet exchanges
            exchange_short = row.get('exchange')
            if exchange_short in ['PNK', 'OTC']:
                continue

            company_name = row.get('longname') or row.get('shortname')
            exchange = row.get('exchDisp') or exchange_short
            sector = row.get('sectorDisp') or row.get('sector', "N/A")
            industry = row.get('industryDisp') or row.get('industry', "N/A")

            out.append({
                "ticker": ticker,
                "company_name": company_name,
                "quote_type": quote_type,
                "exchange": exchange,
                "sector": sector,
                "industry": industry,
            })

        return out

    def search_companies(
        self,
        query: str = "",
        limit: int = 20,
        local: bool = False,
        yq_search_payload: dict | None = None
    ) -> list[dict]:
        """
        Search for companies either locally or online based on the local flag.

        Args:
            query: Company name or ticker to search for
            limit: Maximum number of results to return (default: 20)
            local: If True, search local DB only — fast, no API call (default: False)
            yq_search_payload: Optional raw yq.search() response, passed through
                               to search_companies_online if provided.

        Returns:
            List of company dicts. Returns empty list if no results found.
        """
        query = query.strip()
        if local:
            return self.search_companies_local(query=query, limit=limit)
        return self.search_companies_online(query=query, limit=limit, yq_search_payload=yq_search_payload)

    def search_news(
        self,
        query: str = "",
        limit: int = 10,
        yq_search_payload: dict | None = None
    ) -> list[dict]:
        """
        Search for news stories related to the query.

        If yq_search_payload is provided, extracts news from it directly
        instead of making a new API call. This allows the /search route to reuse
        a single yq.search() response for both companies and news.

        Args:
            query: Search term matched against article titles and related tickers
            limit: Maximum number of stories to return (default: 10)
            yq_search_payload: Optional raw yq.search() response to extract from.
                               If not provided, a new API call will be made.

        Returns:
            List of dicts with keys: search_type, uuid, title, publisher, link,
            providerPublishTime, thumbnail, relatedTickers.
            Returns empty list if no stories found or API is down.
        """
        yqs = YahooQueryService()
        io = APIDataIO()

        if yq_search_payload is None:
            safe_query = str(query).strip()
            yq_search_payload = yqs.yq_search(safe_query, quotes_count=0, news_count=limit)

        if not yq_search_payload:
            logger.warning(f"Yahoo search failed for '{query}' - API may be down")
            return []

        news = yqs.extract_news(yq_search_payload, qty=limit)
        if news:
            io.set_news(news)

            for n in news:
                n["search_type"] = "news"

        return news

    def search_users(self, query: str, report_manager_instance=None) -> list[dict]:
        """
        Search for users by username.

        Args:
            query: Partial or full username to search for
            report_manager_instance: Optional ReportManager instance.
                                     Instantiated internally if not provided.

        Returns:
            List of dicts with keys: search_type, username, snap_datetime,
            cash_balance, portfolio_value, grand_total, rank.
            Returns empty list if no users found.
        """
        if report_manager_instance is None:
            report_manager_instance = ReportManager()

        safe_query = f"%{str(query).strip()}%"
        rows = self.select_query(
            "SELECT id, username FROM users WHERE username LIKE ?",
            (safe_query,)
        )
        if not rows:
            logger.info(f"No users found matching '{query}'")
            return []

        user_ids = [row['id'] for row in rows if row.get('id') is not None]
        user_data = report_manager_instance.get_users_ranks(user_ids=user_ids)

        if user_data:
            for user in user_data:
                user["search_type"] = "users"
                if user.get("user_id") is not None:
                    del user["user_id"]
        
        return user_data