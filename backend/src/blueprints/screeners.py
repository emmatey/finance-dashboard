import logging

from flask import Blueprint, jsonify, request

from APIDataIO import APIDataIO
from StockScreenerManager import SCREENER_CATEGORIES

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
        if screener_name not in row.keys():
            grouped[screener_name] = [row]
        else:
            grouped[screener_name].append(row)

    return jsonify({"success": True, "data": grouped}), 200
