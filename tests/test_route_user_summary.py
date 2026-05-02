import pytest
import os
from DbManager import DbManager

@pytest.fixture(scope="module")
def client(app):
    with app.app_context():
        db = DbManager.get_db()
        with open("src/schema.sql") as f:
            db.executescript(f.read())
            # Seed test db with user_summary mock data.
        with open("tests/seed/user_summary.sql") as f:
            db.executescript(f.read())
    yield app.test_client()

def test_user_summary(client):
    response = client.get("/user/summary?username=emma")
    print(response)
    assert response.status_code == 200