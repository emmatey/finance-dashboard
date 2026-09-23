"""Seed demo data once before starting the web workers."""

import os

from dotenv import load_dotenv

load_dotenv()

if os.getenv("DEMO_MODE", "").lower() != "true":
    raise SystemExit("Refusing to seed demo data: set DEMO_MODE=true first.")

from app import app
from classes.DbManager import DbManager


with app.app_context():
    DbManager().seed_db_with_demo_data()
