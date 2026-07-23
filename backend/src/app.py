import logging
import os
import sys
import time

# External Libraries
from flask import Flask, g, jsonify, request
from flask_session import Session
from werkzeug.exceptions import HTTPException

# Local Application Modules
from Daemon import Daemon
from blueprints.auth import auth_bp
from blueprints.market_overview import market_overview_bp
from blueprints.research import research_bp
from blueprints.scoreboard import scoreboard_bp
from blueprints.screeners import screeners_bp
from blueprints.search import search_bp
from blueprints.trade import trade_bp
from blueprints.user import user_bp


# Configure Logging
#
# Terminal (stdout) defaults to INFO: a clean narrative of what the app is doing
# (requests in/out, pipeline stages, business events) with no per-query/per-item
# noise. Set LOG_LEVEL=DEBUG to see everything (SQL params, raw payloads, etc).
# finance.log always captures WARNING+ regardless of LOG_LEVEL, so nothing is
# lost when running quiet.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Let handlers filter levels, parent level supersedes handlers.

LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

fh = logging.FileHandler('finance.log', mode='a')
fh.setLevel(logging.WARNING)
fh_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(module)s: %(funcName)s: %(message)s")
fh.setFormatter(fh_formatter)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(LOG_LEVEL)
sh_formatter = logging.Formatter("%(levelname)s: %(module)s: %(funcName)s: %(message)s")
sh.setFormatter(sh_formatter)

logger.addHandler(fh)
logger.addHandler(sh)

# Third-party libraries are chatty at DEBUG/INFO (one line per HTTP connection,
# one per request) and would drown out the app's own narrative. Keep them to
# warnings and above regardless of LOG_LEVEL.
for _noisy_logger in ("urllib3", "urllib3.connectionpool", "requests", "werkzeug"):
    logging.getLogger(_noisy_logger).setLevel(logging.WARNING)

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure name of database for production.
app.config["DATABASE"] = "finance.db"

# Register resource blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(trade_bp)
app.register_blueprint(research_bp)
app.register_blueprint(screeners_bp)
app.register_blueprint(search_bp)
app.register_blueprint(market_overview_bp)
app.register_blueprint(scoreboard_bp)


@app.before_request
def log_request_start():
    """Narrate every request as it comes in, so the terminal shows the app working in real time."""
    g._request_start_time = time.perf_counter()
    qs = request.query_string.decode()
    path = f"{request.path}?{qs}" if qs else request.path
    logger.info(f"--> {request.method} {path}")

@app.after_request
def log_request_end(response):
    """Narrate every request as it finishes, with status + duration."""
    duration_ms = (time.perf_counter() - g.get("_request_start_time", time.perf_counter())) * 1000
    logger.info(f"<-- {request.method} {request.path} {response.status_code} ({duration_ms:.0f}ms)")
    return response

@app.after_request
def apply_no_cache_headers(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """
    Safety net for any exception that reaches Flask without being caught and
    logged closer to its source, so a failure is never silent in the terminal.
    """
    if isinstance(e, HTTPException):
        return e
    logger.exception(f"Unhandled exception on {request.method} {request.path}")
    return jsonify({"success": False, "message": "Internal server error, see finance.log"}), 500

@app.teardown_appcontext
def teardown(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
    if exception:
        logger.error(exception)

@app.route("/")
def home():
    filler_page = """
            <body style="background-color: black; color: green;">
                hi mom. Welcome to app.py!
            </body>
        """
    return filler_page