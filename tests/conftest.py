import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from seed import seed_database
from app.services.auth_service import generate_csrf_token

@pytest.fixture
def app():
    # Use in-memory SQLite database for testing
    app = create_app("testing", {
        "TESTING": True,
        "SECRET_KEY": "test-secret-suite",
        "DATABASE_PATH": ":memory:"
    })
    
    with app.app_context():
        # Seed test database with initial fixtures
        seed_database(repo=app.repository)
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_client(app, client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["email"] = "admin@campus.edu"
        sess["role"] = "admin"
        sess["logged_in"] = True
        sess["_csrf_token"] = "test-csrf-token-xyz"
    return client

@pytest.fixture
def student_client(app, client):
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["email"] = "alex.rivers@campus.edu"
        sess["role"] = "student"
        sess["student_id"] = 1
        sess["logged_in"] = True
        sess["_csrf_token"] = "test-csrf-token-xyz"
    return client
