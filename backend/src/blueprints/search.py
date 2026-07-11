import logging

from flask import Blueprint, jsonify, request

from SearchManager import SearchManager
from YahooQueryService import YahooQueryService

logger = logging.getLogger(__name__)

search_bp = Blueprint("search", __name__, url_prefix="/api/search")


@search_bp.route("", methods=["GET"])
def search():
    """
    Returns combined search results across companies, users, and news.

    Query Parameters:
        ?q=str - Search term (required)

    Returns:
        200 - {
            "companies": [{
                ticker: str,
                company_name: str,
                quote_type: str,
                exchange: str,
                sector: str,
                industry: str,
                search_type: "company"
            }],
            "users": [{
                username: str,
                portfolio_value: float,
                cash_balance: float,
                grand_total: float,
                rank: int,
                search_type: "user"
            }],
            "news": [{
                uuid: str,
                title: str,
                publisher: str,
                link: str,
                providerPublishTime: int,
                relatedTickers: list[str],
                search_type: "news"
            }]
        }
        400 - No search term provided
        500 - Server error
    """
    sm = SearchManager()
    yqs = YahooQueryService()

    query = request.args.get("q", None)
    if query is None:
        return jsonify({
            "success": False,
            "message": "Query parameter 'q' i.e. your search term, is required."
        }), 400

    results = {}

    # Get shared search payload
    yq_search_payload = yqs.yq_search(query=query)

    # Search News
    try:
        results["news"] = sm.search_news(query=query, yq_search_payload=yq_search_payload)
    except Exception as e:
        logger.exception(e)
        return jsonify ({
            "success": False,
            "message": "Server error during news pipeline. (/search)"
        }), 500
    # Search Companies
    try:
        results["companies"] = sm.search_companies(query=query, yq_search_payload=yq_search_payload)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error in company pipeline. (/search)"
        }), 500

    # Search Users
    try:
        results["users"] = sm.search_users(query=query)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error in users pipeline. (/search)"
        }), 500

    results["success"] = True
    return jsonify(results), 200

@search_bp.route("/companies", methods=["GET"])
def search_companies():
    """
    Search for companies by ticker symbol or company name.
    Supports a local-only mode for fast datalist population on each keystroke,
    bypassing the Yahoo Finance API and querying only the local database.

    Query Parameters:
        ?q=str          - Search term (required)
        ?limit=int      - Qty of results.
        ?local=bool     - If true, search local DB only (default: false)

    Returns:
        200 - [{
            ticker: str,
            company_name: str,
            quote_type: str,
            exchange: str,
            sector: str,
            industry: str,
            search_type: "company"
        }]
        400 - No search term provided
        500 - Server error
    """
    sm = SearchManager()
    query = request.args.get("q", None)
    limit = request.args.get("limit", 20)
    local = False

    try:
        limit = int(limit)
    except ValueError:
        logger.exception(f"Limit query parameter is invalid '{limit}' was provided. Value must be castable as INT")
        return jsonify({
            "success": False,
            "message": f"Limit query parameter is invalid '{limit}' was provided. Value must be castable as INT"
        }), 400

    if query is None:
        return jsonify({
            "success": False,
            "message": "Query parameter 'q' i.e. your search term, is required."
        }), 400

    local = request.args.get("local")
    if isinstance(local, str):
        local = local.lower().strip()
    if local and local == 'true':
        local = True
    else:
        local = False

    return jsonify({"success": True, "data": sm.search_companies(query=query, limit=limit, local=local)}), 200

@search_bp.route("/users", methods=["GET"])
def search_users():
    """
    Search for users by username.

    Query Parameters:
        ?q=str - Search term (required)

    Returns:
        200 - [{
            username: str,
            portfolio_value: float,
            cash_balance: float,
            grand_total: float,
            rank: int,
            search_type: "user"
        }]
        400 - No search term provided
        500 - Server error
    """
    sm = SearchManager()

    query = request.args.get("q", None)
    if query is None:
        return jsonify({
            "success": False,
            "message": "Query parameter 'q' i.e. your search term, is required."
        }), 400

    res = None
    try:
        res = sm.search_users(query=query)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error..."
        }), 500

    if not res:
        return jsonify({"success": True, "data": []}), 200

    return jsonify({"success": True, "data": res}), 200

@search_bp.route("/news", methods=["GET"])
def search_news():
    """
    Search for news articles by headline text or related ticker symbols.
    Supports a local-only mode for fast datalist population on each keystroke,
    bypassing the Yahoo Finance API and querying only the local database.

    Query Parameters:
        ?q=str          - Search term (required), matched against article titles
        ?limit=int      - Qty of results.
        ?local=bool     - If true, search local DB only (default: false)

    Returns:
        200 - [{
            uuid: str,
            title: str,
            publisher: str,
            link: str,
            providerPublishTime: int,
            relatedTickers: list[str],
            search_type: "news"
        }]
        400 - No search term provided
        500 - Server error
    """
    sm = SearchManager()

    query = request.args.get("q", None)
    limit = request.args.get("limit", 10)
    local = False

    try:
        limit = int(limit)
    except ValueError:
        logger.exception(f"Limit query parameter is invalid '{limit}' was provided. Value must be castable as INT")
        return jsonify({
            "success": False,
            "message": f"Limit query parameter is invalid '{limit}' was provided. Value must be castable as INT"
        }), 400

    if query is None:
        return jsonify({
            "success": False,
            "message": "Query parameter 'q' i.e. your search term, is required."
        }), 400

    local = request.args.get("local")
    if isinstance(local, str):
        local = local.lower().strip()
    if local and local == 'true':
        local = True
    else:
        local = False

    try:
        res = sm.search_news(query=query, limit=limit, local=local)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error during news search. (/search/news)"
        }), 500

    return jsonify({"success": True, "data": res}), 200
