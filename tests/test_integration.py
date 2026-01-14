"""
Integration tests for the User API.
Tests the full flow (Registration -> DB -> Activation) using a real PostgreSQL instance.
"""

import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_db_connection, DatabaseManager
from app.models.user import UserRepo
from app.core.security import get_password_hash

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
async def manage_test_db_pool():
    """Initializes the database pool once for the entire test session."""
    await DatabaseManager.init_pool()
    yield
    await DatabaseManager.close_pool()


# Ensure ALL test functions in this file are marked as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
async def clean_db():
    """
    Cleans the users table before each integration test.
    Only deletes users with an email ending in @example.com.
    """
    async for conn in get_db_connection():
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM users WHERE email LIKE '%%@example.com'")
            await conn.commit()
    yield


@pytest.mark.asyncio
async def test_full_registration_and_activation_flow():
    """
    Tests the complete user journey from registration to activation using a real database.
    """
    # 1. Register a new user
    email = "integration@example.com"
    password = "securepassword"

    # The TestClient handles the FastAPI lifespan (which initializes its own pool)
    reg_response = client.post(
        "/api/v1/register", json={"email": email, "password": password}
    )
    assert reg_response.status_code == 201

    # 2. Manual database check (DAL) to retrieve the generated code
    # We await the async repository call
    user_in_db = await UserRepo.get_by_email(email)
    assert user_in_db is not None
    assert user_in_db["is_active"] is False
    activation_code = user_in_db["activation_code"]

    # 3. Account activation via API (using Basic Auth)
    act_response = client.post(
        "/api/v1/activate", json={"code": activation_code}, auth=(email, password)
    )
    assert act_response.status_code == 200
    assert act_response.json()["message"] == "Account activated successfully"

    # 4. Final database check: the user must be active
    updated_user = await UserRepo.get_by_email(email)
    assert updated_user["is_active"] is True


@pytest.mark.asyncio
async def test_activation_fails_with_wrong_code():
    """Tests that activation fails if an incorrect code is provided."""
    email = "wrongcode@example.com"
    password = "password123"

    client.post("/api/v1/register", json={"email": email, "password": password})

    act_response = client.post(
        "/api/v1/activate", json={"code": "0000"}, auth=(email, password)
    )

    assert act_response.status_code == 400
    assert act_response.json()["detail"] == "Invalid code"


@pytest.mark.asyncio
async def test_activation_fails_after_expiry():
    """Tests that activation fails after the code expiration timestamp."""
    email = "expired@example.com"
    password = "password123"

    expired_time = time.time() - 10

    # We await the direct repository create call
    await UserRepo.create(email, get_password_hash(password), "9999", expired_time)

    act_response = client.post(
        "/api/v1/activate", json={"code": "9999"}, auth=(email, password)
    )

    assert act_response.status_code == 400
    assert act_response.json()["detail"] == "Code expired"


@pytest.mark.asyncio
async def test_health_check_success():
    """
    Tests that the health check returns 200 OK when both DB and SMTP are reachable.
    """
    response = client.get("/api/v1/health")

    # 1. Check status code
    assert response.status_code == 200

    # 2. Check response body
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dependencies"]["database"] == "healthy"
    assert data["dependencies"]["smtp"] == "healthy"
