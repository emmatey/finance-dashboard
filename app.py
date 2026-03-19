import sys
sys.path.append('src')

import helpers
import logging

from datetime import datetime, timezone
from DbManager import DbManager
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_session import Session
from math import ceil
from ReportManager import ReportManager
from AccountManager import AccountManager


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

@app.route("/")
@helpers.login_required
def index():
    """Show portfolio of stocks"""
    db= DbManager()
    user_id = helpers.get_user_id(session)

    # Check if balance snapshots has been updated in the last 24 hrs
    # Update stock prices
    # Query for portfolio
    # Calculate cost basis


    # Writes datapoint for graphs on homepage every 24 hrs.
    helpers.write_to_balance_snapshots(db, user_id)

    graph_dataset = db.query("SELECT snap_datetime, portfolio_value, cash_balance, grand_total\
                       FROM balance_snapshots WHERE user_id=?", (user_id, ))


    return render_template("index.html", stock_query=stock_query, holdings_value=display_holdings_value, \
                           cash_balance=display_cash_balance, grand_total=grand_total, graph_dataset=graph_dataset)


@app.route("/buy", methods=["GET", "POST"])
@helpers.login_required
def buy():
    """Buy shares of stock"""
    pass


@app.route("/sell", methods=["GET", "POST"])
@helpers.login_required
def sell():
    """Sell shares of stock"""
    pass


@app.route("/history")
@helpers.login_required
def history():
    """Show history of transactions"""
    if request.method == "GET":
        user_id = helpers.get_user_id(session)

        # get total page qty
        page_size = 20
        transaction_qty = db.execute(
            "SELECT COUNT(transaction_id) AS count FROM transactions WHERE user_id = ?", user_id
            )[0]['count']
        page_qty = ceil(transaction_qty / page_size) - 1

        # get current page number
        page = int(request.args.get("page", 0))
        if page < 0:
            page = 0
        if page > page_qty:
            page = page_qty

        # query history of transactions for given user.
        transactions_info = db.execute(
            "SELECT t.transaction_datetime, t.action, t.symbol, t.qty, t.unit_price, t.cash_after, p.name, (t.qty * t.unit_price) AS value\
                FROM transactions AS t\
                    LEFT JOIN portfolio AS p on t.symbol = p.symbol\
                        WHERE t.user_id = ?\
                            ORDER BY t.transaction_datetime DESC\
                                LIMIT ? OFFSET ? * ?", user_id, page_size, page_size, page
        )

        return render_template("history.html", transactions_info=transactions_info, page_qty=page_qty, page=page)


@app.route("/quote", methods=["GET", "POST"])
@helpers.login_required
def quote():
    """Get stock quote."""
    pass


@app.route("/research", methods=["GET"])
@helpers.login_required
def research():
    """Show in-depth details about any given stock."""
    if request.method == "GET":
        # Retrieve form value and validate.
        #symbol = request.args.get("research_query", None)
        #if symbol is None:
        #    return(redirect(request.referrer))
#
        #validated_symbol = helpers.validate_symbol(symbol)
        #if validated_symbol is None:
        #    return(redirect(request.referrer))
        #else:
        #    validated_symbol = validated_symbol.get("symbol", None)
#
        ## Request historical prices from yq
        #prices = rh.get_historical_prices(validated_symbol)
        #print(prices)
        news = rh.get_news('mmm')
        print(news)
        prices = (['1741219200', '1752019200'], ['148.70', '158.70'], ['2638500', '1338500'])

        return render_template("research.html", prices=prices)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    pass


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    pass


if __name__ == "__main__":
    # Create background thread that has a persistent app context and db connection
    # use this to update global data, sync live prices, and write user balance_snapshots!

    pass