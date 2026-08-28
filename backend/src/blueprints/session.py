import logging

from flask import Blueprint, jsonify, request, session

from classes.AccountManager import AccountManager
from classes.CommonQueries import CommonQueries
from classes.TransactionManager import TransactionManager

logger = logging.getLogger(__name__)

session_bp = Blueprint("session", __name__, url_prefix="/api/session")

@session_bp.route("/login", methods=["POST"])
def login():
    """
    Logs in an existing user and sets session cookie.

    Request body (JSON):
        username (str): The user's username.
        password (str): The user's password.

    Returns:
        200: Login successful. {"success": True}
        400: Invalid request body. {"success": False, "message": str}
        401: Invalid username or password. {"success": False, "message": str}
    """
    # Checks for request body.
    if not request.is_json:
        return jsonify({"success": False, "message": "Missing JSON in request"}), 400
    am = AccountManager()

    # Extract response body from request.
    request_body = dict(request.json)

    # Extract username and password from request body
    username = str(request_body.get('username', ''))
    password= str(request_body.get('password', ''))

    # Check if username and password are valid
    ret = am.login(username=username, password=password, session=session)
    if ret is False:
        return jsonify({
            "success": False,
            "message": f"Username or password is invalid :("
            }), 401

    # Update user balance/holdings value in db on login.
    tm = TransactionManager()
    user_id = am.get_user_id_from_username(username=username)
    tm.record_balance_snapshot(user_id=user_id)

    return jsonify({"success": True,
                    "message": f"User {username} logged in."}), 200

@session_bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": True, "username": None}), 200
    cc = CommonQueries()
    username = cc.get_username_from_user_id(user_id=user_id)
    email = cc.get_email_from_user_id(user_id=user_id)
    return jsonify({
        "success": True,
        "username": username,
        "email": email }), 200

@session_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logs out a user.

    Response Codes:
        200: Logged out successfully, session clear.
        500: Session unable to be cleared.
    """
    try:
        session.clear()
        return jsonify({"success": True}), 200
    except Exception:
        logger.exception("Session unable to be cleared.")
        return jsonify({"success": False,
                        "message": "Session unable to be cleared..."}), 500
