from fastapi.testclient import TestClient

from app.seed import DEMO_PASSWORD, DEMO_USERNAME


def test_login_with_seeded_demo_user_succeeds(client: TestClient):
    resp = client.post("/auth/login", json={"username": DEMO_USERNAME, "password": DEMO_PASSWORD})
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_fails(client: TestClient):
    resp = client.post("/auth/login", json={"username": DEMO_USERNAME, "password": "wrong-password"})
    assert resp.status_code == 401


def test_login_with_unknown_username_fails(client: TestClient):
    resp = client.post("/auth/login", json={"username": "nobody", "password": "whatever1"})
    assert resp.status_code == 401


def test_register_creates_new_user_and_never_returns_password(client: TestClient):
    resp = client.post("/auth/register", json={"username": "alice", "password": "hunter22"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "alice"
    assert body["id"]
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_username_fails(client: TestClient):
    client.post("/auth/register", json={"username": "bob", "password": "password1"})
    resp = client.post("/auth/register", json={"username": "bob", "password": "different1"})
    assert resp.status_code == 400


def test_register_then_login_succeeds(client: TestClient):
    client.post("/auth/register", json={"username": "carol", "password": "carolpass1"})
    resp = client.post("/auth/login", json={"username": "carol", "password": "carolpass1"})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_protected_endpoint_without_token_returns_401(client: TestClient):
    resp = client.post("/labels", json={"name": "No auth", "color": "#000000"})
    assert resp.status_code == 401


def test_protected_endpoint_with_invalid_token_returns_401(client: TestClient):
    resp = client.post(
        "/labels",
        json={"name": "Bad token", "color": "#000000"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401


def test_protected_endpoint_with_valid_token_succeeds(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/labels", json={"name": "Authed", "color": "#000000"}, headers=auth_headers)
    assert resp.status_code == 201


def test_public_get_endpoints_do_not_require_auth(client: TestClient):
    assert client.get("/projects").status_code == 200
    assert client.get("/labels").status_code == 200
    assert client.get("/members").status_code == 200
    assert client.get("/projects/p-atlas/tasks").status_code == 200
