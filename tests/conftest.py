import pytest
import tempfile
import os
from app import app as flask_app

@pytest.fixture(scope="module")
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    flask_app.config["DATABASE"] = db_path
    flask_app.config["TESTING"] = True
    # Everything before the yield keyword is setup, everything after is teardown.
    yield flask_app
    os.close(db_fd)
    os.unlink(db_path)