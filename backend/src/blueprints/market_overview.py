import logging

from flask import Blueprint, jsonify

from APIDataIO import APIDataIO
from MarketOverviewCoordinator import MarketOverviewCoordinator, SYMBOLS

logger = logging.getLogger(__name__)

market_overview_bp = Blueprint("market_overview", __name__, url_prefix="/api")


@market_overview_bp.route("/market_overview", methods=["GET"])
def market_overview():
    """
    Returns regional market overview data for the homepage.
    Checks freshness and updates if stale before returning.

    Returns:
        200 - [{
            region: str,
            ticker: str,
            company_name: str,
            current_price: float,
            prev_close: float,
            pct_change: float
        }]
        500 - Server error
    """
    io = APIDataIO()
    moc = MarketOverviewCoordinator()

    try:
        moc.initialize_regional_etfs(dbio_instance=io)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error updating regional ETF data. See finance.log for details..."
        }), 500

    try:
        results = io.get_regional_overview(symbols=SYMBOLS)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Database error fetching regional overview. See finance.log for details..."
        }), 500

    return jsonify({"success": True, "data": results}), 200
