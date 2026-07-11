import logging

from flask import Blueprint, jsonify, request

import helpers
from APIDataIO import APIDataIO
from CommonQueries import CommonQueries
from ResearchDataCoordinator import ResearchDataCoordinator
from YahooQueryService import YahooQueryService

logger = logging.getLogger(__name__)

research_bp = Blueprint("research", __name__, url_prefix="/api/research")


@research_bp.route("/local", methods=["GET"])
def research_local():
    """
    Returns cached research data for a given company without making any external API calls.
    Intended for fast initial page load. Call /research/online afterwards for stale tables.

    Fetches: always-fetch tables (symbols, historical_prices, company_profile) plus any
    tables the freshness report marks as still valid.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - All known tables; stale tables have the sentinel value "stale" instead of data.
        400 - No ticker provided
        404 - Ticker not found in local database
        500 - Database error

    Data Format:
        [{table_name: Data | None}, ...]

    Note: Stale tables will show actual data if they happen to be within their freshness
    threshold. All numeric fields may be None if data is unavailable.
    """

    ALWAYS_GET = ["symbols", "historical_prices", "company_profile"]

    rdc = ResearchDataCoordinator()
    io = APIDataIO()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({
            "success": False,
            "message": "No 'ticker' query parameter provided..."
        }), 400
    ticker = ticker.strip().upper()

    fresh_report = rdc.create_research_fresh_report(ticker)
    fresh_tables = [t for t, is_fresh in fresh_report.items() if t != "symbol" and is_fresh is True]
    tables_to_fetch = list(set(ALWAYS_GET) | set(fresh_tables))

    try:
        fetched = rdc.get_research_data(ticker=ticker, tables_to_get=tables_to_fetch, db_io_instance=io)
    except Exception:
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    # 'symbol' is stock ticker, 'symbols' is table containing data about ticker like price and name and exchange.
    all_tables = [t for t in fresh_report if t != "symbol"] + ["symbols"]
    # If table not
    results = {t: fetched.get(t, None) for t in all_tables}
    results["success"] = True # type: ignore

    return jsonify(results), 200

@research_bp.route("/online", methods=["GET"])
def research_online():
    """
    Returns all 'research' data for a given company.
    Serves a flat list of dicts with a "table_name" k:v pair to differentiate.
    Checks yahooquery API for all data not found in DB, or considered "stale".

    Query Parameter:
        ?ticker=str

    Returns:
        200
        404
        500

    Data Format:
            {
        "stock_splits": [{
            "ticker": str,
            "split_date": str,
            "split_ratio": float,
            "last_updated": str
        }],
        "historical_prices": [{
            "ticker": str,
            "price": float,
            "timestamp": int,
            "volume": int
        }],
        "financial_metrics": [{
            "ticker": str,
            "last_updated": str,
            "market_open": float,
            "prev_close": float,
            "market_cap": float,
            "eps": float,
            "beta": float,
            "trailing_pe": float,
            "forward_pe": float,
            "profit_margin": float,
            "shares_outstanding": float,
            "book_value": float,
            "price_to_book": float,
            "dividend_yield": float,
            "fifty_two_week_high": float,
            "fifty_two_week_low": float,
            "fifty_day_average": float,
            "two_hundred_day_average": float,
            "rating": str,
            "analyst_count": int,
            "target_price": float,
            "current_ratio": float,
            "debt_to_equity": float,
            "todays_volume": float,
            "ten_day_avg_volume": float,
            "three_month_avg_volume": float
        }],
        "news": [{
            "uuid": str,
            "title": str,
            "publisher": str,
            "link": str,
            "providerPublishTime": int,
            "thumbnail": str
        }],
        "company_profile": [{
            "ticker": str,
            "company_desc": str,
            "employee_count": int,
            "industry": str,
            "website": str,
            "last_updated": str
        }],
        "insider_trades": [{
            "ticker": str,
            "transaction_date": str,
            "shares": float,
            "transaction_value": float,
            "filer_name": str,
            "filer_relation": str,
            "transaction_text": str,
            "last_updated": str
        }]
    }

    Note: All numeric fields may be None if data is unavailable.
    """

    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({
            "success": False,
            "message": "No 'ticker' query parameter provided..."
        }), 400
    else:
        ticker = ticker.strip().upper()

    try:
        # Update all "stale" tables in DB
        fresh_report = rdc.create_research_fresh_report(ticker)
        rdc.research_data_update_orchestrator(fresh_report, yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"update_table_subset failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    try:
        # Get all research data after refreshing
        results = rdc.get_research_data(ticker=ticker, db_io_instance=io)
    except Exception:
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    results["success"] = True # type: ignore
    return jsonify(results), 200

@research_bp.route("/summary", methods=["GET"])
def research_summary():
    """
    Returns basic company summary. Upserts symbol if new.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - { ticker: str, name: str, price: float }
        400 - No ticker provided
        404 - Ticker not found
        500 - Data missing
    """
    cc = CommonQueries()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    # Skip API call if stock overview already exists in DB
    # This info is refreshed on calls to research_data_update_orchestrator()
    # Price is updated by satan.py background task
    ticker_info_rows = cc.get_stock_basic_overview(tickers=ticker)
    ticker_info = ticker_info_rows[0] if ticker_info_rows else None
    if ticker_info and ticker_info.get("exchange") and ticker_info.get("company_name") and ticker_info.get("quote_type"):
        return jsonify({
            "success": True,
            "quote_type": ticker_info.get("quote_type"),
            "exchange": ticker_info.get("exchange"),
            "ticker": ticker_info.get("ticker"),
            "company_name": ticker_info.get("company_name"),
            "last_price": ticker_info.get("last_price")
        }), 200

    price_module = []
    try:
        price_module = yqs.yq_ticker_fetch_modules(symbols=ticker, modules=["price"])
    except helpers.TickerNotFoundError as e:
        logger.exception(e)
        return jsonify({"success": False, "message": f"{e}"}), 404
    except Exception as e:
        logger.exception(f"research_summary update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500
    io.upsert_symbols(modules_dict=price_module)

    ticker_info_rows = cc.get_stock_basic_overview(tickers=ticker)
    ticker_info = ticker_info_rows[0] if ticker_info_rows else None
    if not ticker_info:
        return jsonify({"success": False, "message": f"Missing data for {ticker}"}), 500

    return jsonify({
        "success": True,
        "quote_type": ticker_info.get("quote_type"),
        "exchange": ticker_info.get("exchange"),
        "ticker": ticker_info.get("ticker"),
        "company_name": ticker_info.get("company_name"),
        "last_price": ticker_info.get("last_price")
    }), 200

@research_bp.route("/company_profile", methods=["GET"])
def research_company_profile():
    """
    Returns company profile data.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - { ticker: str, company_desc: str, industry: str, website: str, employee_count: int }
        400 - No ticker provided
        404 - Ticker not found
        500 - Data missing or database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["company_profile"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_company_profile update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    results = io.get_company_profile(symbols=[ticker])
    if not results:
        return jsonify({"success": False, "message": f"No company profile found for {ticker}"}), 500

    return jsonify({"success": True, **results[0]}), 200

@research_bp.route("/financial_metrics", methods=["GET"])
def research_financial_metrics():
    """
    Returns financial metrics for a company.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - {
            "ticker": str,
            "last_updated": str,
            "market_open": float,
            "prev_close": float,
            "market_cap": float,
            "eps": float,
            "beta": float,
            "trailing_pe": float,
            "forward_pe": float,
            "profit_margin": float,
            "shares_outstanding": float,
            "book_value": float,
            "price_to_book": float,
            "dividend_yield": float,
            "fifty_two_week_high": float,
            "fifty_two_week_low": float,
            "fifty_day_average": float,
            "two_hundred_day_average": float,
            "rating": str,
            "analyst_count": int,
            "target_price": float,
            "current_ratio": float,
            "debt_to_equity": float,
            "todays_volume": float,
            "ten_day_avg_volume": float,
            "three_month_avg_volume": float
        }
        400 - No ticker provided
        404 - Ticker not found
        500 - Data missing or database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["financial_metrics"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_financial_metrics update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    results = io.get_financial_metrics(symbols=[ticker])
    if not results:
        return jsonify({"success": False, "message": f"No financial metrics found for {ticker}"}), 500

    return jsonify({"success": True, **results[0]}), 200

@research_bp.route("/insider_trades", methods=["GET"])
def research_insider_trades():
    """
    Returns insider trading history for a company.

    Query Parameters:
        ?ticker=str
        ?qty=int

    Returns:
        200 - [{ transaction_date, shares, transaction_value, transaction_text, filer_name, filer_relation }]
        400 - No ticker provided
        404 - Ticker not found
        500 - Database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()
    qty = request.args.get("qty", None)

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["insider_trades"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_insider_trades update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    try:
        if qty is not None:
            results = io.get_insider_trades(symbols=[ticker], limit=int(qty))
        else:
            results = io.get_insider_trades(symbols=[ticker])
    except Exception as e:
        logger.exception(f"research_insider_trades db fetch failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    return jsonify({"success": True, "data": results}), 200

@research_bp.route("/historical_prices", methods=["GET"])
def research_historical_prices():
    """
    Returns historical price data for a company.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - [{ ticker, price, timestamp, volume }]
        400 - No ticker provided
        404 - Ticker not found
        500 - Database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["historical_prices"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_historical_prices update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    try:
        results = io.get_historical_prices(symbols=[ticker])
    except Exception as e:
        logger.exception(f"research_historical_prices db fetch failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    return jsonify({"success": True, "data": results}), 200

@research_bp.route("/stock_splits", methods=["GET"])
def research_stock_splits():
    """
    Returns stock split history for a company.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - [{ ticker, split_date, split_ratio, last_updated }]
        400 - No ticker provided
        404 - Ticker not found
        500 - Database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["stock_splits"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_stock_splits update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    try:
        results = io.get_stock_splits(symbols=[ticker])
    except Exception as e:
        logger.exception(f"research_stock_splits db fetch failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    return jsonify({"success": True, "data": results}), 200

@research_bp.route("/news", methods=["GET"])
def research_news():
    """
    Returns latest news stories, optionally filtered by ticker and/or quantity.
    If a ticker is provided, triggers a freshness check and update for that
    company's news before fetching. If no ticker is provided, returns global
    news from the database without triggering an update.

    Query Parameters:
        ?ticker=str  (optional) - Company ticker to filter news by
        ?qty=int     (optional) - Number of stories to return (default: 10)

    Returns:
        200 - [{
            uuid: str,
            title: str,
            thumbnail: str,
            link: str,
            publisher: str,
            providerPublishTime: int
        }, ...]
        200 - [] if no stories found
        400 - qty parameter is not a valid integer
        404 - ticker not found on Yahoo Finance
        500 - server error updating or fetching news

    Note:
        Global news (no ticker) will not reflect live updates until
        NewsAPIManager is implemented.
    """
    rdc = ResearchDataCoordinator()
    yqs = YahooQueryService()
    io = APIDataIO()

    ticker = request.args.get("ticker", None)
    if ticker:
        ticker = str(ticker).strip().upper()
    qty = request.args.get("qty", None)
    if qty:
        try:
            qty = int(qty)
        except (ValueError, TypeError) as e:
            logger.exception(e)
            return jsonify({
                "success": False,
                "message": "qty must be an integer"}), 400

    # Update stories for ticker provided
    if ticker is not None:
        try:
            rdc.update_research_data_subset(ticker=ticker, tables_to_update=["news"], yqs_instance=yqs, db_io_instance=io)
        except helpers.TickerNotFoundError as e:
            logger.exception(e)
            return jsonify({
                "success": False,
                "message": f"Ticker provided '{ticker}' not found."
            }), 404
        except Exception as e:
            logger.exception(e)
            return jsonify({
                "success": False,
                "message": f"Server error, unable to update news data."
            }), 500
    else:
        # TODO (after NewsAPIManager implementation) update global news if no symbol provided.
        pass

    stories = []
    try:
        if ticker and qty:
            stories.extend(io.get_news(symbols=ticker, limit=qty))
        elif ticker and not qty:
            stories.extend(io.get_news(symbols=ticker))
        elif not ticker and qty:
            stories.extend(io.get_news(limit=qty))
        else:
            stories.extend(io.get_news())
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error, unable to fetch news stories from database."
            }), 500

    return jsonify({"success": True, "data": stories}), 200
