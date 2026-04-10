import helpers
import logging
import sys

from AccountManager import AccountManager
from APIDataIO import APIDataIO
from CommonQueries import CommonQueries
from ReportManager import ReportManager
from ResearchDataCoordinator import ResearchDataCoordinator
from TransactionManager import TransactionManager
from YahooQueryService import YahooQueryService
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
@helpers.login_required
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

@app.route("/user/balance_snapshots", methods=["GET"])
@helpers.login_required
def balance_snapshots():
    """
    Returns the 'balance snapshot' history for the provided user.
    Defaults to logged in user if no query parameter is provided.

    Query Parameter:
        username?=<username>

    Returns:
        200 - [{   
            username: str
            snap_datetime: datetime,
            cash_balance: float,
            portfolio_value: float,
            grand_total: float
        }, ...]
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
    
    try:
        rows = rm.get_balance_snapshot_history(user_id=user_id)
    except Exception:
        return jsonify({
            "success": False,
            "message": "Database error... See finance.log for more info"
        }), 500
    
    if len(rows) < 1:
        return jsonify({
            "success": False, 
            "message": f"No balance history for user {cc.get_username_from_user_id(user_id=user_id)} found..."
            }), 200
    else:
        return jsonify(rows), 200


## TRADE ##


@app.route("/trade", methods=["GET", "POST"])
@helpers.login_required
def trade():
    """
    Trade endpoint. Handles both preview (GET) and execution (POST) of buy/sell transactions.

    GET - Returns data to populate the order preview screen.
        Query Parameter: ?ticker=<ticker>
        Checks freshness of financial metrics and upserts symbol if new.
        Returns 404 if ticker not found online.
        Returns 500 if data is missing or corrupt.

    POST - Executes a buy or sell transaction.
        Request Body: { ticker: str, qty: float, transaction_type: str ('buy' | 'sell') }
        Refreshes price before executing.
        Returns 400 if ticker missing, qty missing, transaction_type invalid, or insufficient funds/shares.
        Returns 404 if ticker not found.
        Returns 500 if transaction fails.

    Requires login.
    """
    user_id = session.get("user_id")
    if user_id is None:
       return jsonify({
           "success": False,
           "message": "Unable to find user_id in session"
       }), 500

    if request.method == "GET":
        cc = CommonQueries()
        rdc = ResearchDataCoordinator()
        io = APIDataIO()
        yqs = YahooQueryService()
        
        ticker = request.args.get("ticker", None)
        if not ticker:
            return jsonify({
                "success": False,
                "message": "No 'ticker' query paramater provided..."
            }), 400
        else:
            ticker = ticker.strip().upper()

        rdc.update_table_subset(ticker=ticker,
                                tables_to_update=["financial_metrics"],
                                yqs_instance=yqs,
                                db_io_instance=io)
        if not cc.symbol_exists_in_db(ticker):
            return jsonify({
                "success": False,
                "message": f"Ticker {ticker} not found."
            }), 404
        
        ticker_info = cc.get_stock_basic_overview(symbol=ticker)
        holding_info = cc.get_holding_info_per_user(user_id=user_id, ticker=ticker)
        fin_metrics = io.get_financial_metrics(symbols=[ticker])
        if not isinstance(fin_metrics, list):
            fin_metrics = None
        if fin_metrics and len(fin_metrics) == 1:
            fin_metrics = fin_metrics[0]
        else:
            fin_metrics = None
        
        if ticker_info is None or fin_metrics is None or holding_info is None:
            return jsonify({
                "success": False,
                "message": f"Missing data for {ticker}. (ticker_info or fin_metrics or holding_info)"
            }), 500

        last_price = ticker_info.get("last_price")
        prev_close = fin_metrics.get("prev_close")
        if last_price is None or prev_close is None:
            return jsonify({
                "success": False,
                "message": f"Missing data for {ticker}. (last_price or prev_close)"
            }), 500
            
        return jsonify({
            "ticker": ticker,
            "name": ticker_info.get("company_name"),
            "current_price": last_price,
            "prev_close": prev_close,
            "pct_change_since_close": round(((last_price - prev_close) / prev_close) * 100, 2),
            "fifty_two_week_high": fin_metrics.get("fifty_two_week_high"),
            "fifty_two_week_low": fin_metrics.get("fifty_two_week_low"),
            "market_cap": fin_metrics.get("market_cap"),
            "three_month_avg_volume": fin_metrics.get("three_month_avg_volume"),
            "analyst_count": fin_metrics.get("analyst_count"),
            "rating": fin_metrics.get("rating"),
            "target_price": fin_metrics.get("target_price"),
            "cash_balance": cc.get_balance(user_id=user_id),
            "qty_owned": holding_info.get("qty_owned"),
            "holding_value": holding_info.get("holding_value"),
        }), 200
    
    if request.method == "POST":
        cc = CommonQueries()
        yqs = YahooQueryService()
        io = APIDataIO()
        tm = TransactionManager()

        if not request.is_json:
            return jsonify({
                "success": False, 
                "message": "Missing JSON in request"}), 400
        request_body = dict(request.json)

        ticker = request_body.get("ticker")
        if not ticker:
            return jsonify({
                "success": False,
                "message": "No 'ticker' value provided in request body..."
            }), 400
        
        qty = request_body.get('qty')
        if not qty:
            return jsonify({
                "success": False,
                "message": "No 'qty' value provided in request body..."
            }), 400
        qty = float(qty)

        transaction_type = request_body.get("transaction_type", "").lower().strip()
        if transaction_type not in ["buy", "sell"]:
            return jsonify({
                "success": False,
                "message": "Invalid 'transaction_type'. Must be 'buy' or 'sell'."
            }), 400

        # Refresh price before executing.
        modules = yqs.yq_ticker_fetch_modules(symbols=ticker, modules="price")
        io.upsert_symbols(modules_dict=modules)
    
        if not cc.symbol_exists_in_db(ticker):
           return jsonify({
               "success": False,
               "message": f"Ticker {ticker} not found."
           }), 404
        
        tx_info = None
        if transaction_type == "buy":
            can_afford = tm.check_can_afford(user_id=user_id, ticker=ticker, qty=qty)
            if not can_afford:
                price = cc.get_current_price_from_db(symbol=ticker) or 0
                return jsonify({
                    "success": False,
                    "message": f"Insufficient funds. Balance is {cc.get_balance(user_id=user_id)}, transaction requires {price * qty}."
                }), 400
            tx_info = tm.record_buy(user_id=user_id, ticker=ticker, qty=qty)

        elif transaction_type == "sell":
            can_sell = tm.check_can_sell(user_id=user_id, ticker=ticker, qty=qty)
            if not can_sell:
                return jsonify({
                    "success": False,
                    "message": f"Insufficient shares. Cannot sell {qty} shares of {ticker}."
                }), 400
            tx_info = tm.record_sell(user_id=user_id, ticker=ticker, qty=qty)

        if tx_info is not None:
            tm.record_balance_snapshot(user_id=user_id)
            return jsonify(tx_info), 200
        else:
            return jsonify({
                "success": False,
                "message": "Transaction unsuccessful, see finance.log"
            }), 500

    return jsonify({"success": False, "message": "Method not allowed"}), 405



    ## RESEARCH ##


@app.route("/research", methods=["GET"])
def research():
    """
    Returns all 'research' data for a given company.
    Serves a flat list of dicts with a "table_name" k:v pair to differentiate. 

    Query Paramater:
        ?ticker=str

    Returns:
        200 -
        404 -

    Data Format:
            {
        "stock_splits": [{
            "ticker": str,
            "split_date": str,
            "split_ratio": float,
            "last_updated": str
        }],
        "historical_prices": [{
            "ticker": str,
            "price": float,
            "timestamp": int,
            "volume": int
        }],
        "financial_metrics": [{
            "ticker": str,
            "last_updated": str,
            "market_open": float,
            "prev_close": float,
            "market_cap": float,
            "eps": float,
            "beta": float,
            "trailing_pe": float,
            "forward_pe": float,
            "profit_margin": float,
            "shares_outstanding": float,
            "book_value": float,
            "price_to_book": float,
            "dividend_yield": float,
            "fifty_two_week_high": float,
            "fifty_two_week_low": float,
            "fifty_day_average": float,
            "two_hundred_day_average": float,
            "rating": str,
            "analyst_count": int,
            "target_price": float,
            "current_ratio": float,
            "debt_to_equity": float,
            "todays_volume": float,
            "ten_day_avg_volume": float,
            "three_month_avg_volume": float
        }],
        "news": [{
            "uuid": str,
            "title": str,
            "publisher": str,
            "link": str,
            "providerPublishTime": int,
            "thumbnail": str
        }],
        "company_profile": [{
            "ticker": str,
            "company_desc": str,
            "employee_count": int,
            "industry": str,
            "website": str,
            "last_updated": str
        }],
        "insider_trades": [{
            "ticker": str,
            "transaction_date": str,
            "shares": float,
            "transaction_value": float,
            "filer_name": str,
            "filer_relation": str,
            "transaction_text": str,
            "last_updated": str
        }]
    }

    Note: All numeric fields may be None if data is unavailable.
    """
    cc = CommonQueries()
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({
            "success": False,
            "message": "No 'ticker' query paramater provided..."
        }), 400
    else:
        ticker = ticker.strip().upper()

    try:
        fresh_report = rdc.create_research_fresh_report(ticker)
        rdc.research_data_update_orchestrator(fresh_report)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception:
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    try:
        results = rdc.get_research_data(ticker=ticker, db_io_instance=io)
    except Exception:
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    return jsonify(results), 200
    

@app.route("/")
def home():
    filler_page = """
            <body style="background-color: black; color: green;">
                hi mom. Welcome to app.py!
            </body>
        """
    return filler_page
