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
from UserManager import UserManager



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
    if request.method == "GET":
        rm = ReportManager()

        user_id = helpers.get_user_id(session)

        balance_raw = rm.get_balance(user_id)
        balance_formatted = helpers.usd(balance_raw)

        # Check if user was redirected from /quote's 'purchase' button and insert the search query if so
        quote_term = request.args.get("symbol", "")

        return render_template("buy.html", balance_formatted=balance_formatted, balance_raw=balance_raw, symbol=quote_term)

    if request.method == "POST":
        symbol = request.form.get("symbol", None)
        shares_input = request.form.get("shares")
        user_id = helpers.get_user_id(session)
        unit_price = None
        name = None

        # Validate form input
        if not shares_input or not shares_input.isdigit():
            return helpers.apology("Shares must be a positive integer", 400)

        # qty = int(shares_input) Support fractional shares!

        if qty <= 0:
            return helpers.apology("Shares must be at least 1", 400)

        # Check if symbol corresponds to an extant stock.
        # lookup() interface == "{'name': 'Macy's Inc Common Stock', 'price': 12.15, 'symbol': 'M'}"
        stock_info = helpers.validate_symbol(symbol)
        if not stock_info:
            return redirect(url_for("buy"))

        # Redefine vars for db write.
        symbol = stock_info.get("symbol", None)
        unit_price = stock_info.get("price", None)
        name = stock_info.get("name", None)

        # Begin transaction to ensure all queries are fulfilled.
        db.execute("BEGIN TRANSACTION")

        # Check if user can afford purchase.
        balance = helpers.get_cash_balance(db, user_id)
        if balance is None:
            db.execute("ROLLBACK")
            return helpers.apology("Database error: Balance not found.")
        transaction_price = (unit_price * qty)
        cash_after = balance - transaction_price

        if transaction_price > balance:
            db.execute("ROLLBACK")
            return helpers.apology(f"Insufficent Balance: The transaction of {qty} shares of {symbol} costs {transaction_price}, but your balance is {balance}.", 400)
        else:
            # Update user's cash balance in users table.
            db.execute("UPDATE users SET cash = ? WHERE id = ?",
                       cash_after, user_id)

        # Update the user portfolio table.
        check_own = db.execute(
            "SELECT * FROM portfolio WHERE symbol = ? AND user_id = ?", symbol, user_id)
        if check_own:
            db.execute("UPDATE portfolio SET shares = (shares + ?), unit_price = ? WHERE symbol = ? AND user_id = ?",
                       qty, unit_price, symbol, user_id)
        else:
            db.execute("INSERT INTO portfolio (user_id, symbol, name, shares, unit_price) VALUES (?, ?, ?, ?, ?)",
                       user_id, symbol, name, qty, unit_price)

        # Write transaction to transactions table
        db.execute(
            "INSERT INTO transactions (user_id, action, symbol, qty, unit_price, cash_after)\
            VALUES (?, 'buy', ?, ?, ?, ?)", user_id, symbol, qty, unit_price, cash_after)

        helpers.write_to_balance_snapshots(db, user_id, force=True)

        # end transaction and save
        db.execute("COMMIT")

        # redirect home
        flash(f"Purchase Sucessful! You bought {qty} share(s) of {symbol} for {helpers.usd(unit_price * qty)}.")

        return redirect(url_for("index"))


@app.route("/sell", methods=["GET", "POST"])
@helpers.login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Validate Input
        try:
            qty = int(request.form.get("shares", None))
        except (ValueError, TypeError) as e:
            print(e)
            return apology("Invalid input: The 'shares' field must contain a number.")
        if qty is None:
            return helpers.apology("Input not found: Please enter a number in the 'shares' field.")
        if qty <= 0:
            return helpers.apology("Invalid input: Invalid quantity for sell order, enter a positive number.")

        symbol = request.form.get("symbol")
        stock_info = helpers.validate_symbol(symbol)

        if not stock_info:
            return redirect(url_for("sell"))

        # Check if user owns stock.
        user_id = helpers.get_user_id(session)
        stock_query = db.execute(
            "SELECT symbol, name, shares, unit_price FROM portfolio WHERE user_id = ? AND symbol = ?", user_id, symbol)
        if not stock_query:
            return helpers.apology(f"Transaction failed. Your portfolio does not contain any shares of {symbol}.")

        # Check if user owns more shares than they're selling.
        shares_owned = int(stock_query[0]["shares"])
        if shares_owned < qty:
            return helpers.apology(f"Transaction failed. You requested to sell {qty} shares but you only own {shares_owned}.")

        db.execute("BEGIN TRANSACTION")

        # Get latest price.
        unit_price = stock_info["price"]

        # Update portfolio table. We can assume stock exists in portfolio from earlier query.
        db.execute("UPDATE portfolio SET shares = (shares - ?), unit_price = ? WHERE user_id = ? AND SYMBOL = ?",
                   qty, unit_price, user_id, symbol.upper())

        # Clean up rows where user sells all shares
        db.execute(
            "DELETE FROM portfolio WHERE user_id = ? AND symbol = ? AND shares = 0",
            user_id, symbol.upper()
        )

        transaction_value = unit_price * qty
        cash_balance = helpers.get_cash_balance(db, user_id)
        cash_after = cash_balance + transaction_value

        db.execute("UPDATE users SET cash = (cash + ?) WHERE id = ?",
                   transaction_value, user_id)

        db.execute("INSERT INTO transactions (user_id, action, symbol, qty, unit_price, cash_after)\
                   VALUES (?, ?, ?, ?, ?, ?)", user_id, 'sell', symbol.upper(), qty, unit_price, cash_after)

        helpers.write_to_balance_snapshots(db, user_id, force=True)

        db.execute("COMMIT")

        flash(f"Sale Sucessful! You sold {qty} share(s) of {symbol} for {helpers.usd(unit_price * qty)}.")

        # Send argument used to trigger CSS effect.
        return redirect(url_for("index", sold="true"))

    if request.method == "GET":
        user_id = helpers.get_user_id(session)

        balance_raw = helpers.get_cash_balance(db, user_id)
        balance_formatted = helpers.usd(balance_raw)

        # Select stock portfolio to provide <option>s in jinja for <select> element.
        stock_query = db.execute(
            "SELECT symbol, name, shares, unit_price FROM portfolio WHERE user_id = ?", user_id)

        return render_template("sell.html", balance_formatted=balance_formatted, balance_raw=balance_raw, stock_query=stock_query)


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
    if request.method == "GET":
        return render_template("quote.html")

    if request.method == "POST":
        # helpers.py 'lookup()' method return format
        # {
        #    "name": quote_data["companyName"],
        #    "price": quote_data["latestPrice"],
        #    "symbol": symbol.upper()
        # }
        query = request.form.get("symbol")
        info = helpers.validate_symbol(query)

        if not info:
            return redirect(url_for("quote"))

        name=info["name"]
        symbol=info["symbol"]
        price=info["price"]

        return render_template("quoted.html", name=name, symbol=symbol, price=price)


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
    UM = UserManager(session)

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return helpers.apology("must provide username", 403)
        elif not password:
            return helpers.apology("must provide password", 403)

        if UM.login(username, password):
            # Redirect user to home page
            return redirect(url_for("index"))
        else:
            return helpers.apology("invalid username and/or password", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


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
    UM = UserManager(session)

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        confirmation = request.form.get("confirmation", None)

        if not username or not password or not confirmation:
            return helpers.apology("Please fill out all fields in the registration form and try again.", 400)
        if password != confirmation:
            return helpers.apology("Password and confirmation are not equal.", 400)

        if UM.register(username, password):
            return redirect(url_for("login"))
        else:
            return helpers.apology("Username already in use.", 400)


    if request.method == "GET":
        return render_template("register.html")


if __name__ == "__main__":
    # Create background thread that has a persistent app context and db connection
    # use this to update global data, sync live prices, and write user balance_snapshots!

