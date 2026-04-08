from fastapi.testclient import TestClient

from app.main import app


def test_register_and_me():
    client = TestClient(app)
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "auth@example.com", "password": "ChangeMe123"},
    )
    assert register.status_code in {200, 409}
    token = register.json().get("access_token") if register.status_code == 200 else None

    if not token:
        token_response = client.post(
            "/api/v1/auth/token",
            data={"username": "auth@example.com", "password": "ChangeMe123"},
        )
        assert token_response.status_code == 200
        token = token_response.json()["access_token"]

    me = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "auth@example.com"


def test_login_rejects_bad_password():
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={"email": "pwcheck@example.com", "password": "RightPass123"},
    )
    login = client.post(
        "/api/v1/auth/token",
        data={"username": "pwcheck@example.com", "password": "WrongPass123"},
    )
    assert login.status_code == 401


def test_register_same_email_twice():
    client = TestClient(app)
    body = {"email": "once@example.com", "password": "ChangeMe123"}
    assert client.post("/api/v1/auth/register", json=body).status_code == 200
    second = client.post("/api/v1/auth/register", json=body)
    assert second.status_code == 409


def test_me_rejects_garbage_token():
    client = TestClient(app)
    r = client.get("/api/v1/me", headers={"Authorization": "Bearer not-a-valid-jwt"})
    assert r.status_code == 401
