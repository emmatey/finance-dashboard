import logging
import os
import sqlite3
import time

from dotenv import load_dotenv
from flask import g, current_app
from functools import wraps
from pathlib import Path
from scripts.logging_utils import fmt_data


logger = logging.getLogger(__name__)

class DbManager:
    """
    Base data access for managing SQLite connections and query execution.
    """
    def __init__(self):
        self.seed_db_with_demo_data()

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
    def get_db():
        """
        Check if 'g' contains a reference to the sqlite3.Connection() object.
        Returning this connection for queries if so, and instantiating a connection if not.
        https://flask.palletsprojects.com/en/stable/appcontext/
        """
        root = DbManager.get_root()
        db_name = current_app.config.get("DATABASE")
        if not db_name:
            raise RuntimeError("Database not found in current_app.config...")
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
                
                # Enable "write-ahead logging" 
                # https://sqlite.org/wal.html
                con.execute("PRAGMA journal_mode=WAL;")

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

    def check_demo_mode(self):
        """
        Checks the .env file for "demo_mode" state.
        """
        load_dotenv()
        demo_mode = False
        demo_mode_str = os.getenv("DEMO_MODE")

        try:
            demo_mode_str = str(demo_mode_str)
            if demo_mode_str.lower() == "true":
                    demo_mode = True
            else:
                    demo_mode = False
        except:
            logger.error("Unable to convert 'demo mode' env var to string. Check it exists in your .env file.")

        return demo_mode

    def set_demo_data_seeded(self, demo_mode: bool):
        """
        Sets the "demo_data_seeded" event in "global_events" table.
        Used to prevent executing the script again to insert the same data.
        """
        if isinstance(demo_mode, bool) == False:
            raise TypeError("demo_mode arg, must be bool.")

        demo_mode_state = None
        if demo_mode is True:
            demo_mode_state = 1
        else:
            demo_mode_state = 0

        self.modify_query(f"""
            UPDATE global_events
            SET demo_data_seeded {demo_mode_state}
            WHERE id = 1
            """)

    def check_demo_data_seeded(self):
        """
        Checks if 'demo data' has already been added to the db.
        This should only happen when demo_mode env var is True.
        """
        rows = self.select_query("""
            SELECT demo_data_seeded
            FROM global_events
            WHERE id = 1
        """)
        seeded = rows[0].get("demo_data_seeded", False)

        if seeded:
            return True
        else:
            return False
        
    def seed_db_with_demo_data(self):
        """
        Inserts demo data, updates global events table.
        """
        # I should probably make this "execute script" action a function, this is number two! Lets wait until I do it once more :P
        def _seed_with_data():
            root = DbManager.get_root()
            schema_path = root / "src" / "seed.sql"

            con = self.get_db()
            cur = con.cursor()
            try:
                with open(schema_path, "r") as f:
                    con.executescript(f.read())
            except Exception:
                con.rollback()
                logger.exception(f"Demo data seeding failed.")
                raise
            finally:
                cur.close()
            ###############################################
            # Im gonna close the connection and get another one from g via the modify query method to make fixing this later easier.
        
        demo_mode = self.check_demo_mode()
        if not demo_mode:
            return

        demo_data_seeded = self.check_demo_data_seeded()
        if demo_data_seeded:
            logger.debug("Demo data already seeded...")
            return

        _seed_with_data()
        self.set_demo_data_seeded(True)

    @time_method
    def select_query(self, query: str, placeholders: tuple = ()) -> list[dict]:
        """
        Handles SELECT and WITH queries, returns results as a list of dicts.

        Arguments:'
        query': SQL literal: str,
        placeholders: tuple of placeholders e.g in the query 'query("SELECT * FROM table WHERE id = ?", (1,))' '?' is the placeholder, and would be
        populated by passing (value, ) to this function

        Returns [{}, {}] i.e. list of rows formatted as dicts {col: val}
        """
        query = query.lstrip()
        con = self.get_db()
        cur = con.cursor()

        try:
            logger.debug(f"Params: {fmt_data(placeholders)}")
            logger.debug(f"Executing SELECT Query: {query}")
            cur.execute(query, placeholders)
            rows = cur.fetchall()
            logger.debug(f"Result: {len(rows)} rows | Data: {fmt_data(rows)}\n")
            return rows

        except Exception:
            con.rollback()
            logger.exception(f"Select query failed  | Params: {placeholders}")
            raise

        finally:
            cur.close()

    @time_method
    def modify_query(self, query: str, placeholders: tuple = ()) -> int:
        """
        Handles non-SELECT queries (INSERT, UPDATE, DELETE, etc.), returns number of rows affected.

        Arguments: 
            'query': SQL literal: str,
            placeholders: tuple of placeholders

        Returns:
          number of rows affected by the query
        """
        query = query.lstrip()
        con = self.get_db()
        cur = con.cursor()

        try:
            logger.debug(f"Params: {fmt_data(placeholders)}")
            logger.debug(f"Executing MODIFY Query: {query}")
            cur.execute(query, placeholders)
            row_count = cur.rowcount
            con.commit()
            logger.debug(f"Result: {row_count} rows affected\n")
            return row_count

        except Exception:
            con.rollback()
            logger.exception(f"Modify query failed  | Params: {placeholders}")
            raise

        finally:
            cur.close()

    @time_method
    def bulk_query(self, query: str, data_list: list[tuple], label: str | None = None):
        """
        Executes a query many times in a single transaction.
        data_list should be a list of tuples.

        Args:
            label: Optional short name (e.g. table name) included in the INFO
                   success line, so consecutive bulk writes are distinguishable
                   in the terminal instead of all reading identically.
        """
        con = self.get_db()
        cur = con.cursor()
        try:
            logger.debug(f"Params: {fmt_data(data_list)}")
            logger.debug(f"Executing Query: {query}")
            cur.executemany(query, data_list)
            con.commit()
            logger.debug(f"Result: {cur.rowcount} rows affected\n")
            tag = f" [{label}]" if label else ""
            logger.info(f"Bulk Query Success{tag}: {cur.rowcount} rows affected.")
            return cur.rowcount
        except Exception:
            con.rollback()
            logger.exception(f"Bulk query failed | Params: {data_list}")
            raise
        finally:
            cur.close()
