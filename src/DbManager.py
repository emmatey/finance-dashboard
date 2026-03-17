import logging
import sqlite3
import time

from flask import g
from functools import wraps
from pathlib import Path
from typing import Union, Dict, Any, List



logger = logging.getLogger(__name__)

class DbManager:
    """
    Base data access for managing SQLite connections and query execution.
    """

    @staticmethod
    def time_method(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time
            logger.debug(f"PERF: {func.__name__} finished in {duration:.4f}s")
            return result
        return wrapper


    @staticmethod
    def get_root(anchor="requirements.txt") -> Path:
        """
        Locates the project root based on the presence of requirements.txt.
        """
        # .resolve() returns the absolute path
        current_path = Path(__file__).resolve()

        for parent in current_path.parents:
            if (parent / anchor).exists():
                logger.debug(f"Project root anchored at: {parent}")
                return parent

        raise RuntimeError(f"Project root not found, missing anchor file {anchor}")


    @staticmethod
    def get_db(db_name="finance.db"):
        """
        Check if 'g' contains a reference to the sqlite3.Connection() object.
        Returning this connection for queries if so, and instantiating a connection if not.
        https://flask.palletsprojects.com/en/stable/appcontext/
        """
        root = DbManager.get_root()
        db_path = root / db_name
        if 'db' not in g:
            try:
                con = sqlite3.connect(db_path)

                # Format values returned by querying cursor or connection objects.
                # https://docs.python.org/3/library/sqlite3.html#how-to-create-and-use-row-factories
                def dict_factory(cursor, row):
                    fields = [column[0] for column in cursor.description]
                    return {key: value for key, value in zip(fields, row)}

                # Enable Row access and Foreign Keys
                con.row_factory = dict_factory
                con.execute("PRAGMA foreign_keys = ON;")

                # Check if the 'insider_trades' table i.e final CREATE TABLE query in schema.sql exists
                cur = con.cursor()
                check = cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='insider_trades'"
                ).fetchone()

                if not check:
                    logger.info("Empty database detected. Running schema.sql...")
                    schema_path = root / "src" / "schema.sql"

                    if not schema_path.exists():
                        logger.error(f"schema.sql not found at {schema_path}")
                        raise FileNotFoundError(f"schema.sql not found at {schema_path}")

                    with open(schema_path, "r") as f:
                        con.executescript(f.read())
                        con.commit()

                cur.close()

                # Store reference to Connection in g object
                g.db = con
                return con

            except Exception as e:
                logger.critical(f"Unable to initialize DB connection to {db_path} {e}")
                raise

        else:
            return g.db


    @time_method
    def simple_query(self, query: str, placeholders: tuple = ()) -> list[dict] | int:
        """
        Handles db queries, manage cursor lifecycle, extract result from
        row datastructure and return as a list of dicts.

        args: 'query': SQL literal: str,
        placeholders: tuple of placeholders e.g in the query 'query("SELECT * FROM table WHERE id = ?", (1,))' '?' is the placeholder, and would be
            populated by passing (value, ) to this function

        SELECT Returns [{}, {}] i.e. list of rows formatted as dicts {col: val} or number of rows effected by non-selects
        """
        query = query.lstrip()
        con = self.get_db()
        cur = con.cursor()
        row_count = 0

        try:
            # Check if query is SELECT
            if query.split(None, 1)[0].upper() in ["SELECT", "WITH"]:
                logger.debug(f"Executing Query: {query} | Params: {placeholders}")
                cur.execute(query, placeholders)
                rows = cur.fetchall()
                return rows

            # If not SELECT, requires transaction.
            else:
                logger.debug(f"Executing Query: {query} | Params: {placeholders}")
                cur.execute(query, placeholders)
                row_count = cur.rowcount
                con.commit()
                return row_count

        except Exception:
            con.rollback()
            logger.exception("Simple query failed")
            raise

        finally:
            cur.close()

    @time_method
    def bulk_query(self, query: str, data_list: list[tuple]):
        """
        Executes a query many times in a single transaction.
        data_list should be a list of tuples.
        """
        con = self.get_db()
        cur = con.cursor()
        try:
            logger.debug(f"Executing Query: {query} | Params: {data_list}")
            cur.executemany(query, data_list)
            con.commit()
            logger.info(f"Bulk Query Success: {cur.rowcount} rows affected.")
            return cur.rowcount
        except Exception:
            con.rollback()
            logger.exception("Bulk query failed")
            raise
        finally:
            cur.close()
