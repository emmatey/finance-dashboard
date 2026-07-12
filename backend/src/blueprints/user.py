import logging

from flask import Blueprint, jsonify, request, session

import helpers
from CommonQueries import CommonQueries
from ReportManager import ReportManager

logger = logging.getLogger(__name__)

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.route("/summary", methods=["GET"])
def user_summary():
    """
    Returns a summary of a user profile. Including username, value of
    cash balance, rank, value of holdings, and the datetime this data was captured.

    Query Parameter:
        ?username=<username>

    Returns:
        400 - Invalid username or no username provided.
        500 - Missing/partial data for username provided.
        200 -    out_data = {
            "username": str,
            "user_id": int,
            "snap_datetime": datetime,
            "portfolio_value": float,
            "cash_balance": float,
            "grand_total": float,
            "rank": int
        } | None
    """
    cc = CommonQueries()
    rm = ReportManager()

    user_id = 0
    try:
        user_id = helpers.get_user_id_from_query_param_or_session(request, session, cc)
    except helpers.UserNotFoundError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 404
    except helpers.NoUserProvidedError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 400

    ret = rm.get_users_ranks(user_ids=[user_id])
    if isinstance(ret, list) and len(ret) < 1:
        return jsonify({
                "success": False,
                "message": f"Unable to retrieve data for username {cc.get_username_from_user_id(user_id=user_id)}."
                }), 500

    user_info = ret[0]
    out_data = {
        "username": user_info.get("username"),
        "user_id": user_info.get("user_id"),
        "snap_datetime": user_info.get("snap_datetime"),
        "portfolio_value": user_info.get("portfolio_value"),
        "cash_balance": user_info.get("cash_balance"),
        "grand_total": user_info.get("grand_total"),
        "rank": user_info.get("rank")
    }
    missing = []
    for k, v in out_data.items():
        if v is None:
            missing.append(k)
    if missing:
        return jsonify({
                "success": False,
                "message": f"Data {missing} not found for user {user_id}"
                }), 500
    else:
        out_data["success"] = True
        return jsonify(out_data), 200

@user_bp.route("/portfolio", methods=["GET"])
def portfolio_view():
    """
    Retrieves a summary of user holdings.
    Returned as a list of objects which each represent one holding.
    If no query parameter is provided, the logged in user will be used.

    Query Parameter:
        username?=<username>

    Returns:
        200 - return_data = [{
                symbol: Ticker symbol,
                name: Company name,
                shares: Number of shares owned (split-adjusted),
                unit_price: Current market price per share,
                cost_basis: Average cost per share (FIFO),
                current_value: Total current value (shares * unit_price),
                total_cost: Total amount paid for shares,
                gain_loss: Dollar gain/loss (current_value - total_cost),
                gain_loss_pct: Percentage gain/loss,
                todays_gain_loss: Dollar gain/loss since previous close,
                todays_gain_loss_pct: Percentage change since previous close,
                market_state: Yahoo market session state, or null if not yet available
            }]
        400 - Username not found in session, nor query parameter.
        404- Username not found in database.
        500 - Database error.
    """
    rm = ReportManager()
    cc = CommonQueries()

    user_id = 0
    try:
        user_id = helpers.get_user_id_from_query_param_or_session(request, session, cc)
    except helpers.UserNotFoundError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 404
    except helpers.NoUserProvidedError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 400

    # try get portfolio view from user ID
    try:
        portfolio_view = rm.get_portfolio_view(user_id=user_id)
    except Exception:
        logger.exception(f"portfolio_view failed for user {user_id}")
        return jsonify({
            "success": False,
            "message": f"Database error..."
        }), 500
    if not portfolio_view:
        return jsonify({"success": True, "data": []}), 200
    else:
        return jsonify({"success": True, "data": portfolio_view}), 200

@user_bp.route("/transactions", methods=["GET"])
@helpers.login_required
def transaction_history():
    """
    Gets the transaction history for the provided user.
    Defaults to logged in user if no query parameter is provided.

    Query Parameter:
        username?=<username>

    Returns:
        200 - [{
                transaction_id: int,
                username: str,
                ticker: str,
                transaction_type: str,
                qty: float,
                unit_price: float,
                datetime: int,
                cash_after: float
            }] | None
        400 - Username not provided
        404 - User not found
        500 - Database error
    """
    cc = CommonQueries()
    rm = ReportManager()

    user_id = 0
    try:
        user_id = helpers.get_user_id_from_query_param_or_session(request, session, cc)
    except helpers.UserNotFoundError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 404
    except helpers.NoUserProvidedError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 400

    tx_history = []
    try:
        tx_history = rm.get_transaction_history(user_id=user_id)
    except Exception:
        logger.exception(f"transaction_history failed for user {user_id}")
        return jsonify({
            "success": False,
            "message": "Database error, see finance.log for more information"}), 500
    if len(tx_history) == 0:
        return jsonify({"success": True, "data": []}), 200

    formatted_response = []
    username = cc.get_username_from_user_id(tx_history[0].get("user_id", 0))
    # Build map of symbol_ids to tickers to reduce db calls for translating symbol_id > human readable symbol
    symbol_id_set = {tx.get("symbol_id") for tx in tx_history if tx.get("transaction_type") not in ['deposit', 'withdraw']}
    placeholders = ", ".join("?" for _ in symbol_id_set)
    sql = f"""
    SELECT id, ticker
    FROM symbols
    WHERE id IN ({placeholders})
    """
    rows = cc.select_query(sql, tuple(symbol_id_set))
    symbol_map = {r.get("id"): r.get("ticker") for r in rows}

    for tx in tx_history:
        formatted_response.append({
            "transaction_id": tx.get("transaction_id"),
            "username": username,
            "ticker": symbol_map.get(tx.get("symbol_id"), "CASH"),
            "transaction_type": tx.get("transaction_type"),
            "qty": tx.get("qty"),
            "unit_price": tx.get("unit_price"),
            "datetime": tx.get("transaction_datetime"),
            "cash_after": tx.get("cash_after")
        })

    return jsonify({"success": True, "data": formatted_response}), 200

@user_bp.route("/balance_snapshots", methods=["GET"])
@helpers.login_required
def balance_snapshots():
    """
    Returns the 'balance snapshot' history for the provided user.
    Defaults to logged in user if no query parameter is provided.

    Query Parameter:
        username?=<username>

    Returns:
        200 - [{
            username: str
            snap_datetime: datetime,
            cash_balance: float,
            portfolio_value: float,
            grand_total: float
        }, ...]
        400 - Username not provided
        404 - User not found
        500 - Database error
    """
    cc = CommonQueries()
    rm = ReportManager()

    user_id = 0
    try:
        user_id = helpers.get_user_id_from_query_param_or_session(request, session, cc)
    except helpers.UserNotFoundError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 404
    except helpers.NoUserProvidedError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 400

    try:
        rows = rm.get_balance_snapshot_history(user_id=user_id)
    except Exception:
        logger.exception(f"balance_snapshots failed for user {user_id}")
        return jsonify({
            "success": False,
            "message": "Database error... See finance.log for more info"
        }), 500

    if len(rows) < 1:
        return jsonify({"success": True, "data": []}), 200
    else:
        return jsonify({"success": True, "data": rows}), 200
