import logging

from flask import Blueprint, jsonify, request

from APIDataIO import APIDataIO
from StockScreenerManager import SCREENER_CATEGORIES, StockScreenerManager

logger = logging.getLogger(__name__)

screeners_bp = Blueprint("screeners", __name__, url_prefix="/api")

# Flat set of every valid screener name, for validating ?screener=.
_ALL_SCREENERS = {name for names in SCREENER_CATEGORIES.values() for name in names}


@screeners_bp.route("/screeners/available", methods=["GET"])
def screeners_available():
    """
    Returns the list of screeners that the frontend can select from, grouped
    by category.

    Returns:
        200 - {"success": True, "data": {category_name: [screener_name, ...], ...}}
    """
    return jsonify({"success": True, "data": SCREENER_CATEGORIES}), 200


@screeners_bp.route("/screeners/fetch", methods=["GET"])
def screeners_fetch():
    """
    Fetch a single screener, a whole category, or everything.

    Query Parameters:
        ?screener=str   - One or more screener names (e.g. 'day_gainers'), repeat
                          the param to request several (?screener=day_gainers&screener=day_losers)
        ?category=str   - A category name from SCREENER_CATEGORIES (e.g. 'movers')
        Provide at most one of 'screener'/'category'. With neither, returns
        every tracked screener.
    Returns:
        200 - {
            screener_name:[{company_data}, ...]
        }
        Company Data Format:
            {
                'screener_name': str,
                'rank': int,
                'ticker': str,
                'company_name': str,
                'current_price': float,
                'prev_close': float,
                'price_change_pct': float,
                'market_cap': float,
                'todays_volume': int,
                'three_month_avg_volume': int,
                'volume_change_pct': float
            }
        400 - Invalid category/screener(s), both given, or bad 'limit'
        500 - Server error
    """
    screener = request.args.getlist("screener")
    category = request.args.get("category")

    if screener and category:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Provide only one of 'screener' or 'category', not both.",
                }
            ),
            400,
        )

    if category:
        if category not in SCREENER_CATEGORIES:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Unknown category '{category}'. See /api/screeners/available for valid categories.",
                    }
                ),
                400,
            )
        screener_names = SCREENER_CATEGORIES[category]
    elif screener:
        unknown = [name for name in screener if name not in _ALL_SCREENERS]
        if unknown:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Unknown screener(s) {unknown}. See /api/screeners/available for valid screeners.",
                    }
                ),
                400,
            )
        screener_names = screener
    else:
        screener_names = None

    try:
        rows = APIDataIO().get_screener_results(screener_names=screener_names)
    except Exception as e:
        logger.exception(e)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Server error fetching screener results. (/screeners/fetch)",
                }
            ),
            500,
        )

    grouped: dict[str, list] = {}
    for row in rows:
        screener_name = str(row.get("screener_name"))
        if screener_name not in grouped:
            grouped[screener_name] = [row]
        else:
            grouped[screener_name].append(row)

    return jsonify({"success": True, "data": grouped}), 200


@screeners_bp.route("/screeners/refresh_custom", methods=["POST"])
def refresh_custom_screeners():
    """
    Recomputes the derived/custom screeners (volume spikes, volume
    compression, insider trading surges) from whatever's currently in
    financial_metrics/insider_trades right now.

    Normally these are recomputed as a side effect of the daemon's screener
    sweep finishing a full pass (see Daemon.update_screener_subset); this
    lets the frontend's Refresh button trigger the same recompute on demand.

    Returns:
        200 - {"success": True}
        500 - one or more of the derived screeners failed to compute
    """
    try:
        ok = StockScreenerManager().refresh_custom_screeners()
    except Exception as e:
        logger.exception(e)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Server error refreshing custom screeners. (/screeners/refresh_custom)",
                }
            ),
            500,
        )

    if not ok:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "One or more custom screeners failed to refresh. See finance.log for details.",
                }
            ),
            500,
        )

    return jsonify({"success": True}), 200
