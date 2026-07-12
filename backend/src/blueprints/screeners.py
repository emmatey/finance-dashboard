import logging

from flask import Blueprint, jsonify

from APIDataIO import APIDataIO
from StockScreenerManager import StockScreenerManager

logger = logging.getLogger(__name__)

screeners_bp = Blueprint("screeners", __name__, url_prefix="/api")


@screeners_bp.route("/screeners/available", methods=["GET"])
def screeners_available():
    """
    Returns the list of screeners that the frontend can select from.
    """
    

@screeners_bp.route("/screeners/fetch", methods=["GET"])
def screeners_fetch():
    """

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
