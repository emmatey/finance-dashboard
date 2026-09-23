"""Seed demo data once before starting the web workers."""

from app import app
from classes.DbManager import DbManager


with app.app_context():
    DbManager().seed_db_with_demo_data()
