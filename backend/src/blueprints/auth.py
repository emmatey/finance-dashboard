import logging

from flask import Blueprint, jsonify, request, session

from AccountManager import AccountManager
from CommonQueries import CommonQueries
from TransactionManager import TransactionManager

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registers a new user.

    Request body (JSON):
        username (str): Alphanumeric, no spaces, min 1 char.
        password (str): ASCII only, min 5 chars, must contain at least
                        one uppercase letter, one lowercase letter, and
                        one non-letter character.

    Returns:
        201: Registration successful. {"success": True}
        400: Invalid request body or validation failure. {"success": False, "message": str}
        409: Username already in use. {"success": False, "message": str}
    """
    # Checks for request body.
    if not request.is_json:
        return jsonify({"success": False, "message": "Missing JSON in request"}), 400

    am = AccountManager()
    request_body = dict(request.json)
    username = str(request_body.get('username', '')).strip()
    password= str(request_body.get('password', ''))

    # Check if username meets website requirements.
    # Username must be ascii and without spaces.
    if not all(char.isascii() and char.isalnum() and char != " " for char in username):
        return jsonify({
            "success": False,
            "message": "Username must be alphanumeric (A-Z, 0-9) with no spaces."
            }), 400
    if len(username) < 1:
        return jsonify({
            "success": False,
            "message": "Username must be at least 1 char long."
            }), 400

    # Check if pw meets website requirements
    # Password must have one capital, one uppercase, one lowercase, and one non-letter, and be 5 chars long.
    if len(password) < 5:
        return jsonify({
            "success": False,
            "message": "Password must be at least 5 chars long."
            }), 400
    if not all((char.isascii() for char in password)):
        # Checks for non-ascii
        return jsonify({
            "success": False,
            "message": "Password must contain only ASCII chars."
            }), 400
    if not any((char.isupper() for char in password)):
        # Checks for uppercase
        return jsonify({
            "success": False,
            "message": "Password must contain at least one uppercase letter."
            }), 400
    if not any((char.islower() for char in password)):
        # Checks for lowercase
        return jsonify({
            "success": False,
            "message": "Password must contain at least one lowercase letter."
            }), 400
    if all((char.isalpha() for char in password)):
        # Checks for non-letters
        return jsonify({
            "success": False,
            "message": "Password must contain at least one non-letter character."
            }), 400

    # Add user to db
    ret = am.register(username=username, password=password)
    if ret == 0:
        return jsonify({
            "success": False,
            "message": f"Username {username} already in use."
            }), 409

    # Return good state
    return jsonify({"success": True}), 201

@auth_bp.route("/login", methods=["POST"])
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

@auth_bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": True, "username": None}), 200
    cc = CommonQueries()
    username = cc.get_username_from_user_id(user_id)
    return jsonify({"success": True, "username": username}), 200

@auth_bp.route("/logout", methods=["POST"])
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
