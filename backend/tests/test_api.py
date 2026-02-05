from fastapi.testclient import TestClient

from app.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def register_and_get_token(client: TestClient) -> str:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "ChangeMe123"},
    )
    assert register.status_code in {200, 409}
    token = None
    if register.status_code == 200:
        token = register.json()["access_token"]
    if not token:
        token_response = client.post(
            "/api/v1/auth/token",
            data={"username": "user@example.com", "password": "ChangeMe123"},
        )
        assert token_response.status_code == 200
        token = token_response.json()["access_token"]
    return token


def test_task_lifecycle():
    client = TestClient(app)
    token = register_and_get_token(client)
    payload = {
        "client_id": "client-001",
        "workflow_type": "invoice_processing",
        "payload": {"invoice_id": 123},
    }
    create = client.post(
        "/api/v1/tasks",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create.status_code == 200
    task_id = create.json()["task_id"]

    status = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert status.status_code == 200
    body = status.json()
    assert body["task_id"] == task_id
    assert body["status"] in {"success", "completed"}
    assert body["result"]["summary"].startswith("MOCK_RESPONSE")


def test_websocket_no_redis():
    client = TestClient(app)
    with client.websocket_connect("/api/v1/ws/updates") as websocket:
        message = websocket.receive_json()
        assert message["status"] == "noop"


def test_me_requires_auth():
    client = TestClient(app)
    response = client.get("/api/v1/me")
    assert response.status_code == 401
