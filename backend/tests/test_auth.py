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
