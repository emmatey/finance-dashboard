import logging

from flask import Blueprint, jsonify
from Daemon import Daemon

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
            "message": "Daemon failed, see finance.log for detials."
        }), 500