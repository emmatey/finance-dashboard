import logging

from flask import Blueprint, jsonify

from ReportManager import ReportManager

logger = logging.getLogger(__name__)

scoreboard_bp = Blueprint("scoreboard", __name__, url_prefix="/api")

# Implement server-side pagination later.
@scoreboard_bp.route("/scoreboard", methods=["GET"])
def scoreboard():
    """
    Returns rankings for all users.

    Returns:
        200 - [{
            username: str,
            portfolio_value: float,
            cash_balance: float,
            grand_total: float,
            rank: int
        }]
        500 - Server error
    """
    rm = ReportManager()

    try:
        results = rm.get_all_users_ranks()
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Database error fetching scoreboard. See finance.log for details..."
        }), 500

    return jsonify({"success": True, "data": results}), 200
