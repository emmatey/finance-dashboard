import logging
import os
import resend

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from itsdangerous import BadData, BadSignature, SignatureExpired
from pathlib import Path
from resend.exceptions import ResendError

from classes.AccountManager import AccountManager
from scripts import helpers

FORGOT_PW_EMAIL_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3]
    / "frontend"
    / "src"
    / "components"
    / "auth"
    / "EmailTemplates"
    / "ForgotPassword.html"
)
VERIFY_EMAIL_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3]
    / "frontend"
    / "src"
    / "components"
    / "auth"
    / "EmailTemplates"
    / "VerifyEmail.html"
)
EMAIL_ALREADY_VERIFIED_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3]
    / "frontend"
    / "src"
    / "components"
    / "auth"
    / "EmailTemplates"
    / "AlreadyVerified.html"
)
FORGOT_PW_TOKEN_MAX_AGE_SECONDS = 10 * 60
EMAIL_FROM_ADDRESS = "onboarding@resend.dev"

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
        400: Missing/malformed request body or validation failure.
             {"success": False, "message": str}
        409: Username or email already in use. {"success": False, "message": str}
        415: Request Content-Type was not application/json.
             {"success": False, "message": str}
    """
    # Checks for request body.
    try:
        request_body = helpers.parse_json_body(request)
    except helpers.InvalidJSONBodyError as e:
        return jsonify({"success": False, "message": str(e)}), e.status_code

    am = AccountManager()
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
        return jsonify({"success": False, "message": f"Username {username} already in use."}), 409
    if email and am.check_email_in_use(email=email):
        return jsonify({"success": False, "message": f"Email {email} already in use."}), 409

    # Add user to db
    am.register(username=username, password=password, email=email)

    # Return good state
    return jsonify({"success": True}), 201


@auth_bp.route("/token/generate/forgot_pw", methods=["POST"])
def generate_and_send_forgot_pw_token():
    """
    Generates a signed, time-limited password-reset token for a user.

    Request body (JSON):
        email (str): Email address of the account to generate a token for.

    Returns:
        200: Request processed. Always returned regardless of whether the
             email is registered, to avoid leaking account existence.
             {"success": True, "message": str}
        400: Missing/malformed request body or missing email.
             {"success": False, "message": str}
        415: Request Content-Type was not application/json.
             {"success": False, "message": str}
        500: Server misconfiguration prevented token generation, or the
             reset email failed to send. {"success": False, "message": str}
    """
    am = AccountManager()

    try:
        request_body = helpers.parse_json_body(request)
    except helpers.InvalidJSONBodyError as e:
        return jsonify({"success": False, "message": str(e)}), e.status_code

    email = request_body.get("email")
    if not email or not isinstance(email, str):
        return jsonify({"success": False, "message": "Must provide email: str in request body"}), 400

    generic_response = (
        jsonify({"success": True, "message": "If that email is registered and validated, a password reset link has been sent."}),
        200,
    )

    user_id = am.get_user_id_from_email(email=email)
    if not user_id:
        # Deliberately indistinguishable from the success path below, to
        # avoid leaking whether an email is registered.
        return generic_response

    verified = am.check_email_validated(email=email)
    if not verified:
        return generic_response

    try:
        signed_token = am.generate_verification_token(context_salt="forgot_pw", email=email, user_id=user_id)
    except Exception:
        logger.exception("Failed to generate verification token due to server misconfiguration.")
        return jsonify({"success": False, "message": "Unable to process request at this time."}), 500

    load_dotenv()
    resend_api_key = os.getenv("RESEND_API_KEY")
    if not resend_api_key:
        logger.error("RESEND_API_KEY not set; cannot send forgot-password email.")
        return jsonify({"success": False, "message": "Unable to process request at this time."}), 500
    resend.api_key = resend_api_key

    username = am.get_username_from_user_id(user_id)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/auth/change?token={signed_token}"
    expires_in = f"{FORGOT_PW_TOKEN_MAX_AGE_SECONDS // 60} minutes"

    html = FORGOT_PW_EMAIL_TEMPLATE_PATH.read_text()
    html = (
        html.replace("{{username}}", username)
        .replace("{{reset_link}}", reset_link)
        .replace("{{expires_in}}", expires_in)
    )

    params: resend.Emails.SendParams = {
        "from": EMAIL_FROM_ADDRESS,
        "to": [email],
        "subject": "Reset your password",
        "html": html,
    }

    try:
        resend.Emails.send(params)
    except ResendError:
        logger.exception(f"Failed to send forgot-password email to {email}.")
        return jsonify({"success": False, "message": "Unable to process request at this time."}), 500

    return generic_response


@auth_bp.route("/token/verify/forgot_pw", methods=["POST"])
def verify_pw_change_token_submit_pw_change():
    """
    Verifies "forgot PW" token, and submits a pw reset if valid.

    Request body (JSON):
        token (str): Signed verification token from the forgot-password email.
        new_password (str): See check_pw_valid for password requirements.

    Returns:
        200: Email verified successfully.
    
    Raises:
        400: InvalidJSONBodyError
        415: InvalidJSONBodyError; Invalid content type
        500: Server misconfiguration prevented token validation, or password
             change failed unexpectedly.
    """
    try:
        request_body = helpers.parse_json_body(request)
    except helpers.InvalidJSONBodyError as e:
        return jsonify({"success": False, "message": str(e)}), e.status_code

    # Validate Token
    am = AccountManager()
    token = request_body.get("token")
    if not token or not isinstance(token, str):
        return jsonify({"success": False, "message": "Must provide token: str in request body"}), 400
    try:
        decrypted_token = am.validate_verification_token(
            context_salt="forgot_pw",
            token=token,
            max_age=FORGOT_PW_TOKEN_MAX_AGE_SECONDS,
        )
    except SignatureExpired:
        return jsonify({"success": False, "message": "Token has expired."}), 400
    except (BadSignature, BadData):
        return jsonify({"success": False, "message": "Invalid token."}), 400
    except TypeError:
        logger.exception(
            "Failed to validate verification token due to server misconfiguration."
        )
        return jsonify({"success": False, "message": "Unable to process request at this time."}), 500

    try:
        user_id = int(decrypted_token.get("user_id") or 0)
    except TypeError:
        return jsonify({"success": False, "message": "Unable to type coerce user_id from token"}), 400

    if not user_id:
        return jsonify({"success": False, "message": "Token did not contain a valid user_id"}), 400

    password = request_body.get("new_password")
    if not isinstance(password, str):
        return jsonify({"success": False, "message": "Must provide new_password: str in request body"}), 400

    password_valid, password_message = am.check_pw_valid(password)
    if not password_valid:
        return jsonify({"success": False, "message": password_message}), 400

    try:
        am.change_password(password=password, user_id=user_id)
    except Exception:
        logger.exception(f"Failed to change password for user_id={user_id}.")
        return jsonify({"success": False, "message": "Unable to process request at this time."}), 500

    return jsonify({
        "success": True,
        "email": am.get_email_from_user_id(user_id),
        "username": am.get_username_from_user_id(user_id)
        }), 200

@auth_bp.route("/token/generate/verify_email", methods=["POST"])
def generate_and_send_email_verify_token():
    """
    Generates a signed, time-limited email-verification token.

    Request body (JSON):
        email (str): Email address of the account to generate a token for.

    Returns:
        200: Request processed.
             {"success": True, "message": str}
        400: Missing/malformed request body or missing email.
             {"success": False, "message": str}
        415: Request Content-Type was not application/json.
             {"success": False, "message": str}
        500: Server misconfiguration prevented token generation, or the
             reset email failed to send. {"success": False, "message": str}
    """
    try:
        request_body = helpers.parse_json_body(request)
    except helpers.InvalidJSONBodyError as e:
        return jsonify({"success": False, "message": str(e)}), e.status_code

    email = request_body.get("email")
    if not email or not isinstance(email, str):
        return jsonify({"success": False, "message": "Must provide email: str in request body"}), 400

    generic_response = (
        jsonify({"success": True, "message": "If that email is associated with a registered user, a validation link has been sent."}),
        200,
    )

    am = AccountManager()

    # Load email API key.
    load_dotenv()
    resend_api_key = os.getenv("RESEND_API_KEY")
    if not resend_api_key:
        logger.error("RESEND_API_KEY not set; cannot send verification email.")
        return jsonify({"success": False, "message": "Unable to process request at this time."}), 500
    resend.api_key = resend_api_key

    # Check if email in use
    in_use = am.check_email_in_use(email=email)
    if not in_use:
        return generic_response

    # Lookup username from email for later use in both email templates.
    user_id = am.get_user_id_from_email(email=email)
    username = am.get_username_from_user_id(user_id)

    # Send the "already verified" email if the account is validated already.
    validated = am.check_email_validated(email=email)
    if validated:
        html = EMAIL_ALREADY_VERIFIED_TEMPLATE_PATH.read_text()
        html = html.replace("{{username}}", username)
        params: resend.Emails.SendParams = {
            "from": EMAIL_FROM_ADDRESS,
            "to": [email],
            "subject": "Verify your email address.",
            "html": html,
        }
        try:
            resend.Emails.send(params)
        except ResendError:
            logger.exception(f"Failed to send verification email to {email}.")
            return jsonify({"success": False, "message": "Unable to process request at this time."}), 500

        return generic_response

    # Generate token with "verify email salt"
    try:
        signed_token = am.generate_verification_token(context_salt="verify_email", email=email, user_id=user_id)
    except Exception:
        logger.exception("Failed to generate verification token due to server misconfiguration.")
        return jsonify({"success": False, "message": "Unable to process request at this time."}), 500

    # Send out verification email
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    verify_link = f"{frontend_url}/auth/verify?token={signed_token}"
    expires_in = f"{FORGOT_PW_TOKEN_MAX_AGE_SECONDS // 60} minutes"

    html = VERIFY_EMAIL_TEMPLATE_PATH.read_text()
    html = (
        html.replace("{{username}}", username)
        .replace("{{verify_link}}", verify_link)
        .replace("{{expires_in}}", expires_in)
    )

    params: resend.Emails.SendParams = {
        "from": EMAIL_FROM_ADDRESS,
        "to": [email],
        "subject": "Verify your email address.",
        "html": html,
    }

    try:
        resend.Emails.send(params)
    except ResendError:
        logger.exception(f"Failed to send verification email to {email}.")
        return jsonify({"success": False, "message": "Unable to process request at this time."}), 500

    # 200
    return generic_response

@auth_bp.route("/token/verify/verify_email", methods=["POST"])
def verify_email_verification_token():
    """
    Verifies "verify email" token, and marks user's email as verified if token is valid.

    Request body (JSON):
        token (str): Signed verification token from the forgot-password email.

    Returns:
        200: Email verified successfully.
    
    Raises:
        400: InvalidJSONBodyError
        415: InvalidJSONBodyError; Invalid content type
        500: Server misconfiguration prevented token validation, or password
             change failed unexpectedly.
    """
    # Validate request body shape and type.
    try:
        request_body = helpers.parse_json_body(request)
    except helpers.InvalidJSONBodyError as e:
        return jsonify({"success": False, "message": str(e)}), e.status_code

    # Validate Token.
    am = AccountManager()
    token = request_body.get("token")
    if not token or not isinstance(token, str):
        return jsonify({"success": False, "message": "Must provide token: str in request body"}), 400
    try:
        decrypted_token = am.validate_verification_token(
            context_salt="verify_email",
            token=token,
            max_age=FORGOT_PW_TOKEN_MAX_AGE_SECONDS,
        )
    except SignatureExpired:
        return jsonify({"success": False, "message": "Token has expired."}), 400
    except (BadSignature, BadData):
        return jsonify({"success": False, "message": "Invalid token."}), 400
    except TypeError:
        logger.exception(
            "Failed to validate verification token due to server misconfiguration."
        )
        return jsonify({"success": False, "message": "Unable to process request at this time."}), 500

    # Extract user ID.
    try:
        user_id = int(decrypted_token.get("user_id") or 0)
    except TypeError:
        return jsonify({"success": False, "message": "Unable to type coerce user_id from token"}), 400
    if not user_id:
        return jsonify({"success": False, "message": "Token did not contain a valid user_id"}), 400

    # Extract email.
    try:
        email = str(decrypted_token.get("email") or "")
    except TypeError:
        return jsonify({"success": False, "message": "Unable to type coerce email from token"}), 400
    if not email:
        return jsonify({"success": False, "message": "Token did not contain a valid user_id"}), 400

    # Mark email as verified.

    # 200