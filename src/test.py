from flask import Flask
from AccountManager import AccountManager
from DbManager import DbManager
from dotenv import load_dotenv
from ResearchDataIO import ResearchDataIO
from ReportManager import ReportManager
from ResearchDataSyncManager import ResearchDataSyncManager
from TransactionManager import TransactionManager
from YahooAPIClient import YahooAPIClient
from ResearchYahooQueryService import ResearchYahooQueryService
from Satan import Satan

import pandas as pd
import datetime
import numpy as np
import yahooquery
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
    io = ResearchDataIO()
    rm = ReportManager()
    sm = ResearchDataSyncManager()
    tm = TransactionManager()
    api = YahooAPIClient()
    yqs = ResearchYahooQueryService()
    dae = Satan()

    



    filler_page = """
        <body style="background-color: black; color: green;">
            hi mom.
        </body>
    """
    return filler_page
