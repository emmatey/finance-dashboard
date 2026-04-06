import helpers
import logging
import sys

from AccountManager import AccountManager
from CommonQueries import CommonQueries
from ReportManager import ReportManager
from TransactionManager import TransactionManager
from flask import Flask, g, request, session, jsonify
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
            "error": "Password must contain at least one non-letter character."
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
            "message": f"Username or password is invalid :("
            }), 401

    # Update user balance/holdings value in db on login.
    tm = TransactionManager()
    user_id = am.get_user_id_from_username(username=username)
    tm.record_balance_snapshot(user_id=user_id)

    return jsonify({"success": True,
                    "message": f"User {username} logged in."}), 200

# Logout
@app.route("/auth/logout", methods=["POST"])
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
        logger.exception("Sesison unable to be cleared.")
        return jsonify({"success": False,
                        "message": "Session unable to be cleared..."}), 500

## USER ##

@app.route("/user/summary", methods=["GET"])
def user_summary():
    """
    Returns a summary of a user profile. Including username, value of
    cash balance, rank, value of holdings, and the datetime this data was caputured.
    
    Query Parameter:
        ?username=<username>
    
    Returns:
        400 - Invalid username or no username provided.
        500 - Missing/partial data for username provided.
        200 -    out_data = {
            "username": str,
            "user_id": int,
            "snap_datetime": datetime,
            "portfolio_value": float,
            "cash_balance": float,
            "grand_total": float,
            "rank": int
        } | None
    """
    cc = CommonQueries()
    rm = ReportManager()
    
    user_id = 0    
    try:
        user_id = helpers.get_user_id_from_query_param_or_session(request, session, cc)
    except helpers.UserNotFoundError as e:
        return jsonify({
            "success": False, 
            "message": str(e)}), 404
    except helpers.NoUserProvidedError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 400

    ret = rm.get_users_ranks(user_ids=[user_id])
    if isinstance(ret, list) and len(ret) < 1:
        return jsonify({
                "success": False,
                "message": f"Unable to retrieve data for username {cc.get_username_from_user_id(user_id=user_id)}."
                }), 500
    
    user_info = ret[0]
    out_data = {
        "username": user_info.get("username"),
        "user_id": user_info.get("user_id"),
        "snap_datetime": user_info.get("snap_datetime"),
        "portfolio_value": user_info.get("portfolio_value"),
        "cash_balance": user_info.get("cash_balance"),
        "grand_total": user_info.get("grand_total"),
        "rank": user_info.get("rank")
    }
    missing = []
    for k, v in out_data.items():
        if v is None:
            missing.append(k)
    if missing:
        return jsonify({
                "success": False,
                "message": f"Data {missing} not found for user {user_id}"
                }), 500
    else:
        out_data["success"] = True
        return jsonify(out_data), 200

@app.route("/user/portfolio", methods=["GET"])
def portfolio_view():
    """
    Retreieves a summary of user holdings.
    Returned as a list of objects which each represent one holding.
    If no query parameter is provided, the logged in user will be used.

    Query Parameter:
        username?=<username>

    Returns:
        200 - return_data = [{
                symbol: Ticker symbol,
                name: Company name,
                shares: Number of shares owned (split-adjusted),
                unit_price: Current market price per share,
                cost_basis: Average cost per share (FIFO),
                current_value: Total current value (shares * unit_price),
                total_cost: Total amount paid for shares,
                gain_loss: Dollar gain/loss (current_value - total_cost),
                gain_loss_pct: Percentage gain/loss
            }]
        400 - Username not found in session, nor query parameter.
        404- Username not found in database.
        500 - Database error.
    """
    rm = ReportManager()
    cc = CommonQueries()
  
    user_id = 0    
    try:
        user_id = helpers.get_user_id_from_query_param_or_session(request, session, cc)
    except helpers.UserNotFoundError as e:
        return jsonify({
            "success": False, 
            "message": str(e)}), 404
    except helpers.NoUserProvidedError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 400

    # try get portfolio view from user ID
    try:
        portfolio_view = rm.get_portfolio_view(user_id=user_id)
    except Exception:
        return jsonify({
            "success": False,
            "message": f"Database error..."
        }), 500
    if not portfolio_view:
        return jsonify({
            "success": True,
            "message": f"Portfolio for user {cc.get_username_from_user_id(user_id=user_id)} empty."
        }), 200
    
    else:
        return portfolio_view, 200

@app.route("/user/transactions", methods=["GET"])
def transaction_history():
    """
    Gets the transaction history for the provided user.
    Defaults to logged in user if no query parameter is provided.

    Query Parameter:
        username?=<username>

    Returns:
        200 - [{
                transaction_id: int,
                username: str,
                ticker: str,
                transaction_type: str,
                qty: float,
                unit_price: float,
                datetime: int,
                cash_after: float
            }] | None
        400 - Username not provided
        404 - User not found
        500 - Database error
    """
    cc = CommonQueries()
    rm = ReportManager()
  
    user_id = 0    
    try:
        user_id = helpers.get_user_id_from_query_param_or_session(request, session, cc)
    except helpers.UserNotFoundError as e:
        return jsonify({
            "success": False, 
            "message": str(e)}), 404
    except helpers.NoUserProvidedError as e:
        return jsonify({
            "success": False,
            "message": str(e)}), 400

    tx_history = []
    try:
        tx_history = rm.get_transaction_history(user_id=user_id)
    except Exception:
        return jsonify({
            "success": False, 
            "message": "Database error, see finance.log for more information"}), 500
    if len(tx_history) == 0:
        return jsonify({
            "success": True,
            "message": f"User {cc.get_username_from_user_id(user_id=user_id)} has no recorded transactions."}), 200
    
    formatted_response = []
    username = cc.get_username_from_user_id(tx_history[0].get("user_id", 0))
    # Build map of symbol_ids to tickers to reduce db calls for translating symbol_id > human readable symbol
    symbol_id_set = {tx.get("symbol_id") for tx in tx_history if tx.get("transaction_type") not in ['deposit', 'withdraw']}
    placeholders = ", ".join("?" for _ in symbol_id_set)
    sql = f"""
    SELECT id, ticker
    FROM symbols
    WHERE id IN ({placeholders})
    """
    rows = cc.select_query(sql, tuple(symbol_id_set))
    symbol_map = {r.get("id"): r.get("ticker") for r in rows}
    
    for tx in tx_history:
        formatted_response.append({
            "transaction_id": tx.get("transaction_id"),
            "username": username,
            "ticker": symbol_map.get(tx.get("symbol_id"), "CASH"),
            "transaction_type": tx.get("transaction_type"),
            "qty": tx.get("qty"),
            "unit_price": tx.get("unit_price"),
            "datetime": tx.get("transaction_datetime"),
            "cash_after": tx.get("cash_after") 
        })
    
    return jsonify(formatted_response), 200

@app.route("/")
def home():
    filler_page = """
            <body style="background-color: black; color: green;">
                hi mom. Welcome to app.py!
            </body>
        """
    return filler_page