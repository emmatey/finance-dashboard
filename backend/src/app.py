import logging
import sys

# External Libraries
from flask import Flask, g
from flask_session import Session

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

# Register resource blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(trade_bp)
app.register_blueprint(research_bp)
app.register_blueprint(screeners_bp)
app.register_blueprint(search_bp)
app.register_blueprint(market_overview_bp)
app.register_blueprint(scoreboard_bp)


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
            dae = Daemon()
            dae.run()
        except Exception:
            logger.exception("Daemon.run() failed during teardown")

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
