import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.seed import DEMO_PASSWORD, DEMO_USERNAME


@pytest.fixture()
def client() -> TestClient:
    """A fresh app + fresh in-memory store (including users/tokens) per test, so tests never
    leak state into each other."""
    app = create_app()
    return TestClient(app)


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    """Bearer-auth headers for the seeded demo user, against the same `client` fixture."""
    resp = client.post("/auth/login", json={"username": DEMO_USERNAME, "password": DEMO_PASSWORD})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
