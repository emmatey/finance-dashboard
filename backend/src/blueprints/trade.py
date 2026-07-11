import logging
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request, session

import helpers
from APIDataIO import APIDataIO
from CommonQueries import CommonQueries
from ResearchDataCoordinator import ResearchDataCoordinator
from TransactionManager import TransactionManager
from YahooQueryService import YahooQueryService

logger = logging.getLogger(__name__)

trade_bp = Blueprint("trade", __name__, url_prefix="/api")


@trade_bp.route("/trade", methods=["GET", "POST"])
@helpers.login_required
def trade():
    """
    Trade endpoint. Handles both preview (GET) and execution (POST) of buy/sell transactions.

    GET - Returns data to populate the order preview screen.
        Query Parameter: ?ticker=<ticker>
        Checks freshness of financial metrics and upserts symbol if new.
        Returns 404 if ticker not found online.
        Returns 500 if data is missing or corrupt.

    POST - Executes a buy or sell transaction.
        Request Body: { ticker: str, qty: float, transaction_type: str ('buy' | 'sell') }
        Refreshes price before executing.
        Returns 400 if ticker missing, qty missing, transaction_type invalid, or insufficient funds/shares.
        Returns 404 if ticker not found.
        Returns 500 if transaction fails.

    Requires login.
    """
    user_id = session.get("user_id")
    if user_id is None:
       return jsonify({
           "success": False,
           "message": "Unable to find user_id in session"
       }), 500

    if request.method == "GET":
        cc = CommonQueries()
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
            rdc.update_research_data_subset(ticker=ticker,
                                    tables_to_update=["financial_metrics"],
                                    yqs_instance=yqs,
                                    db_io_instance=io)
        except helpers.TickerNotFoundError:
            return jsonify({
                "success": False,
                "message": f"Ticker {ticker} not found."
            }), 404
        if not cc.symbol_exists_in_db(ticker):
            return jsonify({
                "success": False,
                "message": f"Ticker {ticker} not found."
            }), 404

        ticker_info = cc.get_stock_basic_overview(tickers=ticker)[0]
        holding_info = cc.get_holding_info_per_user(user_id=user_id, ticker=ticker)
        fin_metrics = io.get_financial_metrics(symbols=[ticker])
        if not isinstance(fin_metrics, list):
            fin_metrics = None
        if fin_metrics and len(fin_metrics) == 1:
            fin_metrics = fin_metrics[0]
        else:
            fin_metrics = None

        if ticker_info is None or fin_metrics is None or holding_info is None:
            return jsonify({
                "success": False,
                "message": f"Missing data for {ticker}. (ticker_info or fin_metrics or holding_info)"
            }), 500

        last_price = ticker_info.get("last_price")
        prev_close = fin_metrics.get("prev_close")
        if last_price is None or prev_close is None:
            return jsonify({
                "success": False,
                "message": f"Missing data for {ticker}. (last_price or prev_close)"
            }), 500

        return jsonify({
            "success": True,
            "ticker": ticker,
            "name": ticker_info.get("company_name"),
            "current_price": last_price,
            "prev_close": prev_close,
            "market_state": ticker_info.get("market_state"),
            "cash_balance": cc.get_balance(user_id=user_id),
            "qty_owned": holding_info.get("qty_owned"),
            "holding_value": holding_info.get("holding_value"),
            "pct_change_since_close": fin_metrics.get("todays_change_pct"),
            "symbol_id": fin_metrics.get("symbol_id"),
            "last_updated": fin_metrics.get("last_updated"),
            "market_open": fin_metrics.get("market_open"),
            "market_cap": fin_metrics.get("market_cap"),
            "eps": fin_metrics.get("eps"),
            "beta": fin_metrics.get("beta"),
            "trailing_pe": fin_metrics.get("trailing_pe"),
            "forward_pe": fin_metrics.get("forward_pe"),
            "profit_margin": fin_metrics.get("profit_margin"),
            "shares_outstanding": fin_metrics.get("shares_outstanding"),
            "book_value": fin_metrics.get("book_value"),
            "price_to_book": fin_metrics.get("price_to_book"),
            "dividend_yield": fin_metrics.get("dividend_yield"),
            "fifty_two_week_high": fin_metrics.get("fifty_two_week_high"),
            "fifty_two_week_low": fin_metrics.get("fifty_two_week_low"),
            "fifty_day_average": fin_metrics.get("fifty_day_average"),
            "two_hundred_day_average": fin_metrics.get("two_hundred_day_average"),
            "rating": fin_metrics.get("rating"),
            "insider_sentiment": fin_metrics.get("insider_sentiment"),
            "analyst_count": fin_metrics.get("analyst_count"),
            "target_price": fin_metrics.get("target_price"),
            "current_ratio": fin_metrics.get("current_ratio"),
            "debt_to_equity": fin_metrics.get("debt_to_equity"),
            "todays_volume": fin_metrics.get("todays_volume"),
            "ten_day_avg_volume": fin_metrics.get("ten_day_avg_volume"),
            "three_month_avg_volume": fin_metrics.get("three_month_avg_volume")
        }), 200

    if request.method == "POST":
        cc = CommonQueries()
        yqs = YahooQueryService()
        io = APIDataIO()
        tm = TransactionManager()

        if not request.is_json:
            return jsonify({
                "success": False,
                "message": "Missing JSON in request"}), 400
        request_body = dict(request.json)

        ticker = request_body.get("ticker")
        if not ticker:
            return jsonify({
                "success": False,
                "message": "No 'ticker' value provided in request body..."
            }), 400

        qty_raw = request_body.get('qty')
        if not qty_raw:
            return jsonify({
                "success": False,
                "message": "No 'qty' value provided in request body..."
            }), 400
        try:
            # enforces 1/10th of a share being the smallest fraction allowed.
            exponent = Decimal(str(qty_raw)).as_tuple().exponent
            if not isinstance(exponent, int) or exponent < -1:
                return jsonify({
                    "success": False,
                    "message": "qty cannot have more than 1 decimal place"
                }), 400
        except InvalidOperation:
            return jsonify({
                "success": False,
                "message": "qty must be a valid number"
            }), 400
        qty = float(qty_raw)

        transaction_type = request_body.get("transaction_type", "").lower().strip()
        if transaction_type not in ["buy", "sell"]:
            return jsonify({
                "success": False,
                "message": "Invalid 'transaction_type'. Must be 'buy' or 'sell'."
            }), 400

        # Refresh price before executing.
        modules = yqs.yq_ticker_fetch_modules(symbols=ticker, modules="price")
        io.upsert_symbols(modules_dict=modules)

        if not cc.symbol_exists_in_db(ticker):
           return jsonify({
               "success": False,
               "message": f"Ticker {ticker} not found."
           }), 404

        ticker_info = cc.get_stock_basic_overview(tickers=ticker)[0]
        market_state = ticker_info.get("market_state")
        if market_state != "REGULAR":
            return jsonify({
                "success": False,
                "message": f"Market is not trading for {ticker} (state: {market_state})."
            }), 400

        tx_info = None
        if transaction_type == "buy":
            can_afford = tm.check_can_afford(user_id=user_id, ticker=ticker, qty=qty)
            if not can_afford:
                price = cc.get_current_price_from_db(symbol=ticker) or 0
                return jsonify({
                    "success": False,
                    "message": f"Insufficient funds. Balance is {cc.get_balance(user_id=user_id)}, transaction requires {price * qty}."
                }), 400
            tx_info = tm.record_buy(user_id=user_id, ticker=ticker, qty=qty)

        elif transaction_type == "sell":
            can_sell = tm.check_can_sell(user_id=user_id, ticker=ticker, qty=qty)
            if not can_sell:
                return jsonify({
                    "success": False,
                    "message": f"Insufficient shares. Cannot sell {qty} shares of {ticker}."
                }), 400
            tx_info = tm.record_sell(user_id=user_id, ticker=ticker, qty=qty)

        if tx_info is not None:
            tm.record_balance_snapshot(user_id=user_id)
            tx_info["success"] = True
            return jsonify(tx_info), 200
        else:
            return jsonify({
                "success": False,
                "message": "Transaction unsuccessful, see finance.log"
            }), 500

    return jsonify({"success": False, "message": "Method not allowed"}), 405
