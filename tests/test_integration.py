"""
Integration tests for the User API.
Tests the full flow (Registration -> DB -> Activation) using a real PostgreSQL instance.
"""

import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_db_connection
from app.core.security import get_password_hash
from app.models.user import UserRepo

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    """
    Cleans the users table before each integration test.
    To avoid potential nightmare in case this test is launched in production
    we only select test users
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE email LIKE '%%@example.com'")
            conn.commit()
    yield


def test_full_registration_and_activation_flow():
    """
    Tests the complete user journey from registration to activation using a real database.
    """
    # 1. Register a new user
    email = "integration@example.com"
    password = "securepassword"

    reg_response = client.post(
        "/api/v1/register", json={"email": email, "password": password}
    )
    assert reg_response.status_code == 201

    # 2. Manual database check (DAL) to retrieve the generated code
    user_in_db = UserRepo.get_by_email(email)
    assert user_in_db is not None
    assert user_in_db["is_active"] is False
    activation_code = user_in_db["activation_code"]

    # 3. Account activation via API (using Basic Auth)
    act_response = client.post(
        "/api/v1/activate", json={"code": activation_code}, auth=(email, password)
    )
    assert act_response.status_code == 200
    assert act_response.json()["message"] == "Account activated successfully"

    # 4. Vérification finale en base : l'utilisateur doit être actif
    updated_user = UserRepo.get_by_email(email)
    assert updated_user["is_active"] is True


def test_activation_fails_with_wrong_code():
    """
    Tests that activation fails if an incorrect code is provided to the database.
    """
    email = "wrongcode@example.com"
    password = "password123"

    # Inscription
    client.post("/api/v1/register", json={"email": email, "password": password})

    # 2. Attempt activation with an incorrect code
    act_response = client.post(
        "/api/v1/activate", json={"code": "0000"}, auth=(email, password)  # Wrong code
    )

    assert act_response.status_code == 400
    assert act_response.json()["detail"] == "Invalid code"

    # Vérification : l'utilisateur est toujours inactif
    user = UserRepo.get_by_email(email)
    assert user["is_active"] is False


def test_activation_fails_after_expiry():
    """
    Tests that activation fails after the code expiration timestamp in the database.
    """
    email = "expired@example.com"
    password = "password123"

    # Simulate a user already in the DB with an expired code
    # (Using Repo directly to manipulate time)

    expired_time = time.time() - 10  # Expired 10 seconds ago

    UserRepo.create(email, get_password_hash(password), "9999", expired_time)

    # Tentative d'activation
    act_response = client.post(
        "/api/v1/activate", json={"code": "9999"}, auth=(email, password)
    )

    assert act_response.status_code == 400
    assert act_response.json()["detail"] == "Code expired"
