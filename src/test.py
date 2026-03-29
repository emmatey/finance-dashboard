from flask import Flask
from CommonQueries import CommonQueries
from AccountManager import AccountManager
from DbManager import DbManager
from dotenv import load_dotenv
from APIDataIO import APIDataIO
from ReportManager import ReportManager
from ResearchDataCoordinator import ResearchDataCoordinator
from TransactionManager import TransactionManager
from YahooAPIClient import YahooAPIClient
from YahooQueryService import YahooQueryService
from Satan import Satan
from MarketOverviewCoordinator import MarketOverviewCoordinator
from SearchManager import SearchManager
import pandas as pd
import datetime
import numpy as np
import yahooquery as yq
import logging
import os
import sys


# export FLASK_APP=test.py
app = Flask(__name__)
load_dotenv()
api_key = os.getenv("NEWS_API_KEY")

@app.route("/")
def home():
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
    ################################################################################
    am = AccountManager()
    db = DbManager()
    io = APIDataIO()
    rm = ReportManager()
    rdc = ResearchDataCoordinator()
    tm = TransactionManager()
    api = YahooAPIClient()
    yqs = YahooQueryService()
    dae = Satan()
    moc = MarketOverviewCoordinator()
    sm = SearchManager()
    cc = CommonQueries()
    
    YQ_SCREENER_NAMES = [
        'day_gainers', 
        'day_losers', 
        'most_actives', 
        'most_watched_tickers', 
        'fifty_two_wk_gainers', 
        'fifty_two_wk_losers'
    ]
    """
    Checks the age of screener data and updates if stale.
    Updates all screeners if data is older than SCREENER_UPDATE_FREQUENCY.
    """
    screeners = yqs.yq_screener_fetch_screeners(screeners=YQ_SCREENER_NAMES, count=1)
    filtered_screeners = yqs._filter_screener_data(screeners)

    # Add custom volume spike screeners
    relative_volumes_screener = yqs.extract_relative_volumes(filtered_screeners)
    filtered_screeners.update(relative_volumes_screener)
    
    # Extract metadata and rankings
    metadata = yqs.extract_screener_metadata(filtered_screeners)
    
    # Extract price and financial data
    price_modules, financial_metrics = yqs.extract_screener_data(filtered_screeners)
    print(price_modules)
    print(financial_metrics)

    ## Upsert symbols first (screener rankings reference symbol_id)
    #io.upsert_symbols(price_modules)
    #
    ## Insert screener rankings (clears table first, so all get same timestamp)
    #io.set_screeners_metadata(metadata)
    #
    ## Update financial metrics (incomplete data, don't update last_updated timestamp)
    #io.set_financial_metrics(financial_metrics, from_screeners=True)
    #logger.info(f"Successfully updated {len(filtered_screeners)} screeners with {len(price_modules)} unique tickers")

    filler_page = """
        <body style="background-color: black; color: green;">
            hi mom.
        </body>
    """
    return filler_page

