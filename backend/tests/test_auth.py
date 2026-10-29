from app.models import User
from app.core.security import hash_password

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.database import get_db

def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 201

    result = response.json()

    assert result["status"] is True
    assert result["data"] == {}
    assert result["status_code"] == 201
    assert result["message"] == "User registered successfully"


def test_register_duplicate_email(client):
    user_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "TestPass123!",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )
    assert second_response.status_code == 409
    assert second_response.json()["message"] == "Email is already registered"


def test_login_user_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Login User",
            "email": "loginuser@example.com",
            "password": "TestPass123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] is True
    assert result["status_code"] == 200
    assert result["message"] == "Login successful"
    assert result["data"]["access_token"]
    assert result["data"]["token_type"] == "bearer"


def test_login_user_invalid_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Login User",
            "email": "wrongpassword@example.com",
            "password": "TestPass123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpassword@example.com",
            "password": "WrongPass123!",
        },
    )

    assert response.status_code == 401
    result = response.json()
        
    assert result["status"] is False
    assert result["data"] == {}
    assert result["status_code"] == 401
    assert result["message"] == "Invalid email or password"


def test_login_user_not_found(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "TestPass123!",
        },
    )

    result = response.json()

    assert result["status"] is False
    assert result["data"] == {}
    assert result["status_code"] == 401
    assert result["message"] == "Invalid email or password"


def test_login_inactive_user(client, db_session):
    user = User(
        name="Inactive User",
        email="inactive@example.com",
        hashed_password=hash_password("TestPass123!"),
        is_active=False,
    )

    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inactive@example.com",
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 401

    result = response.json()

    assert result["status"] is False
    assert result["status_code"] == 401
    assert result["message"] == "Invalid email or password"


def test_get_current_user_with_valid_token(db_session):
    test_app = FastAPI()

    test_app.dependency_overrides[get_db] = lambda: db_session

    @test_app.get("/protected")
    def protected_route(
        current_user: User = Depends(get_current_user),
    ):
        return {"user_id": current_user.id, "email": current_user.email}

    user = User(
        name="Token User",
        email="tokenuser@example.com",
        hashed_password=hash_password("TestPass123!"),
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(subject=str(user.id))

    with TestClient(test_app) as test_client:
        response = test_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["user_id"] == user.id
    assert response.json()["email"] == user.email


def test_get_current_user_with_invalid_token(db_session):
    test_app = FastAPI()

    test_app.dependency_overrides[get_db] = lambda: db_session

    @test_app.get("/protected")
    def protected_route(
        current_user: User = Depends(get_current_user),
    ):
        return {"user_id": current_user.id}

    with TestClient(test_app) as test_client:
        response = test_client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
