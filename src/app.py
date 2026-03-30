import helpers
import logging
import sys

from AccountManager import AccountManager
from flask import Flask, flash, g, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session


# Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # Let handlers filter levels, parent level supersedes handlers.

fh = logging.FileHandler('finance.log', mode='a')
fh.setLevel(logging.WARNING)
fh_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(module)s: %(funcName)s: %(message)s")
fh.setFormatter(fh_formatter)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh_formatter = logging.Formatter("%(levelname)s: %(module)s: %(funcName)s: %(message)s")
sh.setFormatter(sh_formatter)

logger.addHandler(fh)
logger.addHandler(sh)

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = helpers.usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)

    if db is not None:
        db.close()
    if exception:
        logger.error(exception)

### AUTH ###

# Register
@app.route("/auth/register", methods=["POST"])
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
        400: Invalid request body or validation failure. {"success": False, "error": str}
        409: Username already in use. {"success": False, "error": str}
    """
    # Checks for request body.
    if not request.is_json:
        return jsonify({"success": False, "error": "Missing JSON in request"}), 400
    
    am = AccountManager()
    request_body = dict(request.json)
    username = str(request_body.get('username', '')).strip()
    password= str(request_body.get('password', ''))

    # Check if username meets website requirements.
    # Username must be ascii and without spaces.
    if not all(char.isascii() and char.isalnum() for char in username):
        return jsonify({
            "success": False,
            "error": "Username must be alphanumeric (A-Z, 0-9) with no spaces."
            }), 400
    if len(username) < 1:
        return jsonify({
            "success": False,
            "error": "Username must be at least 1 char long."
            }), 400
    
    # Check if pw meets website requirements
    # Password must have one capital, one uppercase, one lowercase, and one non-letter, and be 5 chars long.
    if len(password) < 5:
        return jsonify({
            "success": False,
            "error": "Password must be at least 5 chars long."
            }), 400
    if not all((char.isascii() for char in password)):
        # Checks for non-ascii
        return jsonify({
            "success": False,
            "error": "Password must contain only ASCII chars."
            }), 400
    if not any((char.isupper() for char in password)):
        # Checks for uppercase
        return jsonify({
            "success": False,
            "error": "Password must contain at least one uppercase letter."
            }), 400
    if not any((char.islower() for char in password)):
        # Checks for lowercase
        return jsonify({
            "success": False,
            "error": "Password must contain at least one lowercase letter."
            }), 400
    if all((char.isalpha() for char in password)):
            # Checks for non-letters
        return jsonify({
            "success": False,
            "error": "Password must contain at least one non-letter character."
            }), 400
    
    # Add user to db
    ret = am.register(username=username, password=password)
    if ret == 0:
        return jsonify({
            "success": False,
            "error": f"Username {username} already in use."
            }), 409
    
    # Return good state 
    return jsonify({"success": True}), 201

# Login
@app.route("/auth/login", methods=["POST"])
def login():
    """
    Logs in an existing user and sets session cookie.

    Request body (JSON):
        username (str): The user's username.
        password (str): The user's password.

    Returns:
        200: Login successful. {"success": True}
        400: Invalid request body. {"success": False, "error": str}
        401: Invalid username or password. {"success": False, "error": str}
    """
    # Checks for request body.
    if not request.is_json:
        return jsonify({"success": False, "error": "Missing JSON in request"}), 400
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
            "error": f"Username or password is invalid :("
            }), 401

    return jsonify({"success": True}), 200

# Logout
@app.route("/auth/logout", methods=["POST"])
def logout():
    """
    Logs out a user.
    """
    session.clear()
    return jsonify({"success": True}), 200

## USERS ##

@app.route("/users", methods=["GET"])
def users():
    """
    """
    
    return "hi!"



@app.route("/")
def home():
    filler_page = """
            <body style="background-color: black; color: green;">
                hi mom. Welcome to app.py!
            </body>
        """
    return filler_page