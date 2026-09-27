import logging

from classes.DbManager import DbManager
from classes.Daemon import Daemon
from flask import Blueprint, jsonify


logger = logging.getLogger(__name__)

internal_bp = Blueprint("internal", __name__, url_prefix="/internal")


@internal_bp.route("/daemon", methods=["POST"])
def run_daemon():
    """
    Runs Daemon.py class' Daemon.run() method.
    This class does various background tasks like updating pricing data, updating screener data,
    updating the news, cleaning the db, and taking snapshots of user account states.

    These requests are all scheduled and executed by the daemon class and this endpoint just exists
    so that an external script can request this happens.

    Returns:
        200
        500
    """
    dae = Daemon()

    try:
        dae.run()
        return jsonify({"success": True}), 200
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Daemon failed, see finance.log for details."
        }), 500

@internal_bp.route("/demo", methods=["GET"])
def check_demo_mode():
    """
    Checks the environment variables to see if the app is in 'demo mode'. 
    This will change some things about what the frontend looks like.

    Returns:
        200 - {"success": True, "demo_mode": bool}
        500 - Backend exception thrown
    """
    try:
        demo_mode = DbManager.check_demo_mode()
    except Exception:
        logger.exception("Failed to check demo mode")
        return jsonify({
            "success": False,
            "message": "Failed to check demo mode. See finance.log for details..."
        }), 500

    return jsonify({"success": True, "demo_mode": demo_mode}), 200
