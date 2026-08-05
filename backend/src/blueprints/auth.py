import logging

from flask import Blueprint, jsonify, request
from itsdangerous import BadData, BadSignature, SignatureExpired
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from classes.AccountManager import AccountManager

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registers a new user. Assumes email has been verified.

    Request body (JSON):
        username (str): Alphanumeric, no spaces, min 1 char.
        password (str): ASCII only, min 5 chars, must contain at least
                        one uppercase letter, one lowercase letter, and
                        one non-letter character.
        email (str, optional): Email address to associate with the account.

    Returns:
        201: Registration successful. {"success": True}
        400: Invalid request body or validation failure. {"success": False, "message": str}
        409: Username or email already in use. {"success": False, "message": str}
    """
    # Checks for request body.
    if not request.is_json:
        return jsonify({"success": False, "message": "Missing JSON in request"}), 400

    am = AccountManager()
    request_body = dict(request.json)
    username = str(request_body.get("username", "")).strip()
    password = str(request_body.get("password", ""))
    email = request_body.get("email")
    email = email.strip() if isinstance(email, str) else None
    email = email or None

    username_valid, username_message = am.check_username_valid(username)
    if not username_valid:
        return jsonify({"success": False, "message": username_message}), 400
    password_valid, password_message = am.check_pw_valid(password)
    if not password_valid:
        return jsonify({"success": False, "message": password_message}), 400
    if am.get_user_id_from_username(username=username):
        return (
            jsonify(
                {"success": False, "message": f"Username {username} already in use."}
            ),
            409,
        )
    if email and am.check_email_in_use(email=email):
        return (
            jsonify({"success": False, "message": f"Email {email} already in use."}),
            409,
        )

    # Add user to db
    am.register(username=username, password=password, email=email)

    # Return good state
    return jsonify({"success": True}), 201


@auth_bp.route("/token/generate/forgot_pw", methods=["GET"])
def generate_and_send_forgot_pw_token():
    am = AccountManager()

    email = request.args.get("email")
    if not email:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Must provide ?email=<str> query parameter.",
                }
            ),
            400,
        )

    user_id = am.get_user_id_from_email(email=email)
    if not user_id:
        return (
            jsonify({"success": False, "message": f"No user found for email {email}."}),
            400,
        )

    try:
        signed_token = am.generate_verification_token(
            context_salt="forgot_pw", email=email, user_id=user_id
        )
    except TypeError:
        logger.exception(
            "Failed to generate verification token due to server misconfiguration."
        )
        return (
            jsonify(
                {"success": False, "message": "Unable to process request at this time."}
            ),
            500,
        )

    return jsonify({"success": True, "data": signed_token}), 200


@auth_bp.route("/token/verify/pw_change_request", methods=["GET"])
def verify_signed_token_pw_change_request():
    """
    This route is used to verify at token, and then redirect the user to a form to enter their new pw.
    """
    am = AccountManager()

    token = request.args.get("token")
    if not token:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Must provide ?token=<str> query parameter.",
                }
            ),
            400,
        )

    try:
        decrypted_token = am.validate_verification_token(
            context_salt="forgot_pw", token=token
        )
    except SignatureExpired:
        return jsonify({"success": False, "message": "Token has expired."}), 400
    except (BadSignature, BadData):
        return jsonify({"success": False, "message": "Invalid token."}), 400
    except TypeError:
        logger.exception(
            "Failed to validate verification token due to server misconfiguration."
        )
        return (
            jsonify(
                {"success": False, "message": "Unable to process request at this time."}
            ),
            500,
        )

    return jsonify({"success": True, "data": decrypted_token}), 200


@auth_bp.route("/token/verify/pw_change_submit", methods=["POST"])
def verify_signed_token_pw_change_submit():
    """
    This route is used to verify at token again, and then submit a password change.
    """
    # Validate Request
    token = request.args.get("token")
    if not token:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Must provide ?token=<str> query parameter.",
                }
            ),
            400,
        )

    try:
        request_body = dict(request.get_json())
    except UnsupportedMediaType:
        return jsonify({"success":False,"error": "Content-Type must be application/json"}), 415
    except BadRequest:
        return jsonify({"success":False,"error": "Malformed JSON"}), 400
    except TypeError:
        return jsonify({"success": False, "error": "Malformed Request Body"}), 400

    # Validate Token
    am = AccountManager()
    try:
        decrypted_token = am.validate_verification_token(
            context_salt="forgot_pw", token=token
        )
    except SignatureExpired:
        return jsonify({"success": False, "message": "Token has expired."}), 400
    except (BadSignature, BadData):
        return jsonify({"success": False, "message": "Invalid token."}), 400
    except TypeError:
        logger.exception(
            "Failed to validate verification token due to server misconfiguration."
        )
        return (
            jsonify(
                {"success": False, "message": "Unable to process request at this time."}
            ),
            500,
        )
    
    try:
        user_id = int(decrypted_token.get("user_id") or 0)
    except TypeError:
        return jsonify({"success": False, "message": "Unable to type coerce user_id from token"}), 400

    if not user_id:
        return jsonify({"success": False, "message": "Token did not contain a valid user_id"}), 400

    password = request_body.get("new_password")
    if not isinstance(password, str):
        return (
            jsonify(
                {"success": False, "message": "Must provide new_password: str in request body"}
            ),
            400,
        )

    password_valid, password_message = am.check_pw_valid(password)
    if not password_valid:
        return jsonify({"success": False, "message": password_message}), 400

    try:
        am.change_password(password=password, user_id=user_id)
    except Exception:
        logger.exception(f"Failed to change password for user_id={user_id}.")
        return (
            jsonify(
                {"success": False, "message": "Unable to process request at this time."}
            ),
            500,
        )

    return jsonify({"success": True}), 200
