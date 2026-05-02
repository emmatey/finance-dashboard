import helpers
import logging
import sys

# External Libraries
from flask import Flask, g, jsonify, request, session
from flask_session import Session

# Local Application Modules
from AccountManager import AccountManager
from APIDataIO import APIDataIO
from CommonQueries import CommonQueries
from MarketOverviewCoordinator import MarketOverviewCoordinator, SYMBOLS
from ReportManager import ReportManager  # Fixed space in filename
from ResearchDataCoordinator import ResearchDataCoordinator
from Satan import Satan
from SearchManager import SearchManager
from TransactionManager import TransactionManager
from YahooQueryService import YahooQueryService


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

# Configure name of database for production.
app.config["DATABASE"] = "finance.db"


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.teardown_appcontext
def teardown(exception):
    if not app.config.get("TESTING", False):
        try:
            dae = Satan()
            dae.run()
        except Exception:
            logger.exception("Satan.run() failed during teardown")

    db = g.pop('db', None)
    if db is not None:
        db.close()
    if exception:
        logger.error(exception)

### AUTH ###

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
        return jsonify([]), 200
    
    else:
        return jsonify(portfolio_view), 200

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

        rdc.update_research_data_subset(ticker=ticker,
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
            tx_info["success"] = True
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
        200 
        404 
        500 

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
        rdc.research_data_update_orchestrator(fresh_report, yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"update_table_subset failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    try:
        results = rdc.get_research_data(ticker=ticker, db_io_instance=io)
    except Exception:
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    return jsonify(results), 200

@app.route("/research/summary", methods=["GET"])
def research_summary():
    """
    Returns basic company summary. Upserts symbol if new.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - { ticker: str, name: str, price: float }
        400 - No ticker provided
        404 - Ticker not found
        500 - Data missing
    """
    cc = CommonQueries()
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["financial_metrics"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_summary update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    ticker_info = cc.get_stock_basic_overview(symbol=ticker)
    if not ticker_info:
        return jsonify({"success": False, "message": f"Missing data for {ticker}"}), 500

    return jsonify({
        "ticker": ticker_info.get("ticker"),
        "name": ticker_info.get("company_name"),
        "price": ticker_info.get("last_price")
    }), 200

@app.route("/research/company_profile", methods=["GET"])
def research_company_profile():
    """
    Returns company profile data.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - { ticker: str, company_desc: str, industry: str, website: str, employee_count: int }
        400 - No ticker provided
        404 - Ticker not found
        500 - Data missing or database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["company_profile"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_company_profile update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    results = io.get_company_profile(symbols=[ticker])
    if not results:
        return jsonify({"success": False, "message": f"No company profile found for {ticker}"}), 500

    return jsonify(results[0]), 200

@app.route("/research/financial_metrics", methods=["GET"])
def research_financial_metrics():
    """
    Returns financial metrics for a company.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - {
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
        }
        400 - No ticker provided
        404 - Ticker not found
        500 - Data missing or database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["financial_metrics"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_financial_metrics update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    results = io.get_financial_metrics(symbols=[ticker])
    if not results:
        return jsonify({"success": False, "message": f"No financial metrics found for {ticker}"}), 500

    return jsonify(results[0]), 200

@app.route("/research/insider_trades", methods=["GET"])
def research_insider_trades():
    """
    Returns insider trading history for a company.

    Query Parameters:
        ?ticker=str
        ?qty=int

    Returns:
        200 - [{ transaction_date, shares, transaction_value, transaction_text, filer_name, filer_relation }]
        400 - No ticker provided
        404 - Ticker not found
        500 - Database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()
    qty = request.args.get("qty", None)

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["insider_trades"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_insider_trades update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    try:
        if qty is not None:
            results = io.get_insider_trades(symbols=[ticker], limit=int(qty))
        else:
            results = io.get_insider_trades(symbols=[ticker])
    except Exception as e:
        logger.exception(f"research_insider_trades db fetch failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    return jsonify(results), 200

@app.route("/research/historical_prices", methods=["GET"])
def research_historical_prices():
    """
    Returns historical price data for a company.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - [{ ticker, price, timestamp, volume }]
        400 - No ticker provided
        404 - Ticker not found
        500 - Database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["historical_prices"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_historical_prices update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    try:
        results = io.get_historical_prices(symbols=[ticker])
    except Exception as e:
        logger.exception(f"research_historical_prices db fetch failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    return jsonify(results), 200

@app.route("/research/stock_splits", methods=["GET"])
def research_stock_splits():
    """
    Returns stock split history for a company.

    Query Parameter:
        ?ticker=str

    Returns:
        200 - [{ ticker, split_date, split_ratio, last_updated }]
        400 - No ticker provided
        404 - Ticker not found
        500 - Database error
    """
    rdc = ResearchDataCoordinator()
    io = APIDataIO()
    yqs = YahooQueryService()

    ticker = request.args.get("ticker", None)
    if not ticker:
        return jsonify({"success": False, "message": "No 'ticker' query parameter provided."}), 400
    ticker = ticker.strip().upper()

    try:
        rdc.update_research_data_subset(ticker=ticker, tables_to_update=["stock_splits"], yqs_instance=yqs, db_io_instance=io)
    except helpers.TickerNotFoundError:
        return jsonify({"success": False, "message": f"Ticker {ticker} not found."}), 404
    except Exception as e:
        logger.exception(f"research_stock_splits update failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Error updating data, see finance.log"}), 500

    try:
        results = io.get_stock_splits(symbols=[ticker])
    except Exception as e:
        logger.exception(f"research_stock_splits db fetch failed for {ticker}: {e}")
        return jsonify({"success": False, "message": "Database error, see finance.log"}), 500

    return jsonify(results), 200

## NEWS ##

@app.route("/research/news", methods=["GET"])
def research_news():
    """
    Returns latest news stories, optionally filtered by ticker and/or quantity.
    If a ticker is provided, triggers a freshness check and update for that
    company's news before fetching. If no ticker is provided, returns global
    news from the database without triggering an update.

    Query Parameters:
        ?ticker=str  (optional) - Company ticker to filter news by
        ?qty=int     (optional) - Number of stories to return (default: 10)

    Returns:
        200 - [{
            uuid: str,
            title: str,
            thumbnail: str,
            link: str,
            publisher: str,
            providerPublishTime: int
        }, ...]
        200 - [] if no stories found
        400 - qty parameter is not a valid integer
        404 - ticker not found on Yahoo Finance
        500 - server error updating or fetching news
    
    Note:
        Global news (no ticker) will not reflect live updates until
        NewsAPIManager is implemented.
    """
    rdc = ResearchDataCoordinator()
    yqs = YahooQueryService()
    io = APIDataIO()

    ticker = request.args.get("ticker", None)
    if ticker:
        ticker = str(ticker).strip().upper()
    qty = request.args.get("qty", None)
    if qty:
        try:
            qty = int(qty)
        except (ValueError, TypeError) as e:
            logger.exception(e)
            return jsonify({
                "success": False, 
                "message": "qty must be an integer"}), 400
        
    # Update stories for ticker provided
    if ticker is not None:
        try:
            rdc.update_research_data_subset(ticker=ticker, tables_to_update=["news"], yqs_instance=yqs, db_io_instance=io)
        except helpers.TickerNotFoundError as e:
            logger.exception(e)
            return jsonify({
                "success": False,
                "message": f"Ticker provided '{ticker}' not found."
            }), 404
        except Exception as e:
            logger.exception(e)
            return jsonify({
                "success": False,
                "message": f"Server error, unable to update news data."
            }), 500
    else:
        # TODO (after NewsAPIManager implementation) update global news if no symbol provided.
        pass
    
    stories = []
    try:
        if ticker and qty:
            stories.extend(io.get_news(symbols=ticker, limit=qty))
        elif ticker and not qty:
            stories.extend(io.get_news(symbols=ticker))
        elif not ticker and qty:
            stories.extend(io.get_news(limit=qty))
        else:
            stories.extend(io.get_news())
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error, unable to fetch news stories from database."
            }), 500
    
    return jsonify(stories), 200

## SCREENERS ##

@app.route("/screeners")
def screeners():
    """
    Updates (if stale, defined in MarketOverviewCoordinator class) screener data
    and returns information about screened companies organized by screener. 

    Query Parameters:
        None

    Returns:
        200 - {
            screener_name:[{company_data}, ...]
        }
        Company Data Format:
            {
                'screener_name': str,
                'rank': int,
                'ticker': str,
                'company_name': str,
                'current_price': float,
                'prev_close': float,
                'price_change_pct': float,
                'market_cap': float,
                'todays_volume': int,
                'three_month_avg_volume': int,
                'volume_change_pct': float
            }
        500 - Server error
    """
    io = APIDataIO()
    moc = MarketOverviewCoordinator()

    # Update screeners
    try:
        moc.screener_data_update_orchestrator(dbio_instance=io)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error, unable to update screeners. See finance.log for details..."
        }), 500
    
    # Get screeners
    screener_data = []
    try:
        screener_data = io.get_screener_results()
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Database error, unable to retrieve screener data. See finance.log for details..."
        }), 500

    # Return
    grouped = {}
    broken = []
    for screener in screener_data:
        screener_name = screener.get("screener_name")
        if not screener_name:
            broken.append(screener)
            logger.warning(f"Screener {screener} is malformed, doesn't contain screener_name field.")
            continue
        else:
            try:
                grouped[screener_name].append(screener)
            except KeyError:
                grouped[screener_name] = [screener]
    
    if broken:
        grouped['broken'] = broken
        return jsonify(grouped), 200
    else:
        return jsonify(grouped), 200

@app.route("/search", methods=["GET"])
def search():
    """
    Returns combined search results across companies, users, and news.

    Query Parameters:
        ?q=str - Search term (required)

    Returns:
        200 - {
            "companies": [{
                ticker: str,
                company_name: str,
                quote_type: str,
                exchange: str,
                sector: str,
                industry: str,
                search_type: "company"
            }],
            "users": [{
                username: str,
                portfolio_value: float,
                cash_balance: float,
                grand_total: float,
                rank: int,
                search_type: "user"
            }],
            "news": [{
                uuid: str,
                title: str,
                publisher: str,
                link: str,
                providerPublishTime: int,
                relatedTickers: list[str],
                search_type: "news"
            }]
        }
        400 - No search term provided
        500 - Server error
    """
    sm = SearchManager()
    yqs = YahooQueryService()

    query = request.args.get("q", None)
    if query is None:
        return jsonify({
            "success": False,
            "message": "Query paramater 'q' i.e. your search term, is required."
        }), 400
    
    results = {}

    # Get shared search payload
    yq_search_payload = yqs.yq_search(query=query)

    # Search News
    try:
        results["news"] = sm.search_news(query=query, yq_search_payload=yq_search_payload)
    except Exception as e:
        logger.exception(e)
        return jsonify ({
            "success": False,
            "message": "Server error during news pipeline. (/search)"
        }), 500
    # Search Companies
    try:
        results["companies"] = sm.search_companies(query=query, yq_search_payload=yq_search_payload)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error in company pipeline. (/search)"
        }), 500

    # Search Users
    try:
        results["users"] = sm.search_users(query=query)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error in users pipeline. (/search)"
        }), 500

    return jsonify(results), 200

@app.route("/search/companies", methods=["GET"])
def search_companies():
    """
    Search for companies by ticker symbol or company name.
    Supports a local-only mode for fast datalist population on each keystroke,
    bypassing the Yahoo Finance API and querying only the local database.

    Query Parameters:
        ?q=str          - Search term (required)
        ?limit=int      - Qty of results.
        ?local=bool     - If true, search local DB only (default: false)

    Returns:
        200 - [{
            ticker: str,
            company_name: str,
            quote_type: str,
            exchange: str,
            sector: str,
            industry: str,
            search_type: "company"
        }]
        400 - No search term provided
        500 - Server error
    """
    sm = SearchManager()
    query = request.args.get("q", None)
    limit = request.args.get("limit", 20)
    local = False

    try:
        limit = int(limit)
    except ValueError:
        logger.exception(f"Limit query parameter is invalid '{limit}' was provided. Value must be castable as INT")
        return jsonify({
            "success": False,
            "message": f"Limit query parameter is invalid '{limit}' was provided. Value must be castable as INT"
        }), 400
    
    if query is None:
        return jsonify({
            "success": False,
            "message": "Query paramater 'q' i.e. your search term, is required."
        }), 400
    
    local = request.args.get("local")
    if isinstance(local, str):
        local = local.lower().strip()
    if local and local == 'true':
        local = True
    else:
        local = False

    return jsonify(sm.search_companies(query=query, limit=limit, local=local)), 200

@app.route("/search/users", methods=["GET"])
def search_users():
    """
    Search for users by username.

    Query Parameters:
        ?q=str - Search term (required)

    Returns:
        200 - [{
            username: str,
            portfolio_value: float,
            cash_balance: float,
            grand_total: float,
            rank: int,
            search_type: "user"
        }]
        400 - No search term provided
        500 - Server error
    """
    sm = SearchManager()

    query = request.args.get("q", None)
    if query is None:
        return jsonify({
            "success": False,
            "message": "Query paramater 'q' i.e. your search term, is required."
        }), 400

    res = None
    try:
        res = sm.search_users(query=query)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error..."
        }), 500
    
    if not res:
        return jsonify({
            "success": True,
            "message": f"User {query} not found."
        }), 200
    
    return jsonify(res), 200

@app.route("/search/news", methods=["GET"])
def search_news():
    """
    Search for news articles by headline text or related ticker symbols.

    Query Parameters:
        ?q=str - Search term (required), matched against article titles
                 and related ticker symbols
        ?limit=int      - Qty of results.

    Returns:
        200 - [{
            uuid: str,
            title: str,
            publisher: str,
            link: str,
            providerPublishTime: int,
            relatedTickers: list[str],
            search_type: "news"
        }]
        400 - No search term provided
        500 - Server error
    """
    sm = SearchManager()

    query = request.args.get("q", None)
    limit = request.args.get("limit", 20)

    try:
        limit = int(limit)
    except ValueError:
        logger.exception(f"Limit query parameter is invalid '{limit}' was provided. Value must be castable as INT")
        return jsonify({
            "success": False,
            "message": f"Limit query parameter is invalid '{limit}' was provided. Value must be castable as INT"
        }), 400
    
    if query is None:
        return jsonify({
            "success": False,
            "message": "Query paramater 'q' i.e. your search term, is required."
        }), 400
    
    res = None
    try:
        res = sm.search_news(query=query, limit=limit)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error..."
        }), 500
    
    if res is None or not res:
        return jsonify({
            "success": True,
            "message": f"News related to {query} not found."
        }), 200

    return jsonify(res), 200

## MARKET OVERVIEW ##

@app.route("/market_overview", methods=["GET"])
def market_overview():
    """
    Returns regional market overview data for the homepage.
    Checks freshness and updates if stale before returning.

    Returns:
        200 - [{
            region: str,
            ticker: str,
            current_price: float,
            prev_close: float,
            pct_change: float
        }]
        500 - Server error
    """
    io = APIDataIO()
    moc = MarketOverviewCoordinator()

    try:
        moc.initialize_regional_etfs(dbio_instance=io)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Server error updating regional ETF data. See finance.log for details..."
        }), 500

    try:
        results = io.get_regional_overview(symbols=SYMBOLS)
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Database error fetching regional overview. See finance.log for details..."
        }), 500

    return jsonify(results), 200

## SCOREBOARD ##

@app.route("/scoreboard", methods=["GET"])
def scoreboard():
    """
    Returns rankings for all users.

    Returns:
        200 - [{
            username: str,
            portfolio_value: float,
            cash_balance: float,
            grand_total: float,
            rank: int
        }]
        500 - Server error
    """
    rm = ReportManager()

    try:
        results = rm.get_all_users_ranks()
    except Exception as e:
        logger.exception(e)
        return jsonify({
            "success": False,
            "message": "Database error fetching scoreboard. See finance.log for details..."
        }), 500

    return jsonify(results), 200

@app.route("/")
def home():
    filler_page = """
            <body style="background-color: black; color: green;">
                hi mom. Welcome to app.py!
            </body>
        """
    return filler_page