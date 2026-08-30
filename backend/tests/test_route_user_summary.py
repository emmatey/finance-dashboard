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


def test_session_me_exposes_verified_flag(client):
    response = client.get("/api/session/me")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert "verified" in payload
    assert payload["verified"] is False