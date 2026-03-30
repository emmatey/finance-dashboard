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

### Account Actions ###

# Register
@app.route("/register", methods=["POST"])
def register():
    """
    Registers a new user.
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
            "error": "Username must contain only ASCII chars."
            }), 400
    
    # Check if pw meets website requirements
    # Password must have one capital, one uppercase, one lowercase, and one non-letter, and be 5 chars long.
    if len(password) < 5:
        # Checks for non-ascii
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
@app.route("/login", methods=["POST"])
def login():
    """

    """

    return "hello"

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    """
    Logs out a user and redirects.
    """
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():
    filler_page = """
            <body style="background-color: black; color: green;">
                hi mom. Welcome to app.py!
            </body>
        """
    from AccountManager import AccountManager
    am = AccountManager()
    print(am.register(username="jerma", password="123"))
    return filler_page