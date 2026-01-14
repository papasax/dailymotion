import time
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_user_repo():
    # We mock UserRepo in deps.py because that's where it's called by the auth dependency.
    # We also mock it in endpoints.py for direct calls like register/set_active.
    with patch("app.api.deps.UserRepo") as mock_deps, \
         patch("app.api.endpoints.UserRepo") as mock_endpoints:
        
        # Synchronize both mocks to share the same behavior
        mock_deps.get_by_email = mock_endpoints.get_by_email
        yield mock_endpoints

def test_register_success(mock_user_repo):
    # Setup mock: User does not exist
    mock_user_repo.get_by_email.return_value = None
    
    response = client.post(
        "/api/v1/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    assert response.status_code == 201
    assert "User registered" in response.json()["message"]
    assert mock_user_repo.create.called

def test_register_already_exists(mock_user_repo):
    # Setup mock: User already exists
    mock_user_repo.get_by_email.return_value = {"email": "test@example.com"}
    
    response = client.post(
        "/api/v1/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_activate_success(mock_user_repo):
    # Setup mock: Valid user, correct code, not expired
    from app.core.security import get_password_hash
    
    mock_user_repo.get_by_email.return_value = {
        "email": "test@example.com",
        "password_hash": get_password_hash("password123"),
        "activation_code": "1234",
        "code_expires_at": time.time() + 60,
        "is_active": False
    }
    
    response = client.post(
        "/api/v1/activate",
        json={"code": "1234"},
        auth=("test@example.com", "password123")
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Account activated successfully"
    assert mock_user_repo.set_active.called

def test_activate_expired_code(mock_user_repo):
    # Setup mock: Valid user, correct code, but EXPIRED
    from app.core.security import get_password_hash
    
    mock_user_repo.get_by_email.return_value = {
        "email": "test@example.com",
        "password_hash": get_password_hash("password123"),
        "activation_code": "1234",
        "code_expires_at": time.time() - 10, # 10 seconds ago
        "is_active": False
    }
    
    response = client.post(
        "/api/v1/activate",
        json={"code": "1234"},
        auth=("test@example.com", "password123")
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Code expired"

def test_activate_wrong_auth(mock_user_repo):
    # Setup mock: User exists but password is different
    from app.core.security import get_password_hash
    
    mock_user_repo.get_by_email.return_value = {
        "email": "test@example.com",
        "password_hash": get_password_hash("correct_password")
    }
    
    response = client.post(
        "/api/v1/activate",
        json={"code": "1234"},
        auth=("test@example.com", "wrong_password")
    )
    
    assert response.status_code == 401
