from flask import Flask
from classes.CommonQueries import CommonQueries
from classes.StockScreenerManager import StockScreenerManager
from classes.AccountManager import AccountManager
from classes.DbManager import DbManager
from dotenv import load_dotenv
from classes.APIDataIO import APIDataIO
from classes.ReportManager import ReportManager
from classes.ResearchDataCoordinator import ResearchDataCoordinator
from classes.TransactionManager import TransactionManager
from classes.YahooAPIClient import YahooAPIClient
from classes.YahooQueryService import YahooQueryService
from classes.Daemon import Daemon
from classes.MarketOverviewCoordinator import MarketOverviewCoordinator
from classes.SearchManager import SearchManager
from classes.NewsAPIManager import NewsAPIManager
import pandas as pd
import datetime
import numpy as np
import yahooquery as yq
import logging
import os
import sys

# export FLASK_APP=test.py
app = Flask(__name__)
app.config["DATABASE"] = "finance.db"
app.config["TESTING"] = True
load_dotenv()
api_key = os.getenv("NEWS_API_KEY")


@app.route("/")
def home():
    # Configure Logging
    logger = logging.getLogger()
    logger.setLevel(
        logging.DEBUG
    )  # Let handlers filter levels, parent level supersedes handlers.

    fh = logging.FileHandler("finance.log", mode="a")
    fh.setLevel(logging.WARNING)
    fh_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s: %(module)s: %(funcName)s: %(message)s"
    )
    fh.setFormatter(fh_formatter)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh_formatter = logging.Formatter(
        "%(levelname)s: %(module)s: %(funcName)s: %(message)s"
    )
    sh.setFormatter(sh_formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)
    ################################################################################
    am = AccountManager()
    db = DbManager()
    io = APIDataIO()
    rm = ReportManager()
    rdc = ResearchDataCoordinator()
    tm = TransactionManager()
    api = YahooAPIClient()
    yqs = YahooQueryService()
    dae = Daemon()
    moc = MarketOverviewCoordinator()
    sm = SearchManager()
    cc = CommonQueries()
    ssm = StockScreenerManager()
    new = NewsAPIManager()


    ret = new.fetch_and_cache_headlines()
    if ret is not None:
        print(ret)
    else:
        print("no return val")
    
    filler_page = """
        <body style="background-color: black; color: green;">
            hi mom! welcome to test.py
        </body>
    """
    return filler_page
