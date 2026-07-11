import logging

from flask import Blueprint, jsonify

from APIDataIO import APIDataIO
from MarketOverviewCoordinator import MarketOverviewCoordinator

logger = logging.getLogger(__name__)

screeners_bp = Blueprint("screeners", __name__, url_prefix="/api")


@screeners_bp.route("/screeners")
def screeners():
    """
    Updates (if stale, defined in MarketOverviewCoordinator class) screener data
    and returns information about screened companies organized by screener.

    Query Parameters:
        None

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
        500 - Server error
    """
    io = APIDataIO()
    moc = MarketOverviewCoordinator()

    # Update screeners
    try:
        moc.screener_data_update_orchestrator(dbio_instance=io)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error, unable to update screeners. See finance.log for details..."
        }), 500

    # Get screeners
    screener_data = []
    try:
        screener_data = io.get_screener_results()
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Database error, unable to retrieve screener data. See finance.log for details..."
        }), 500
    return jsonify(screener_data), 200
