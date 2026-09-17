from fastapi.testclient import TestClient


def test_list_members_returns_seed_data(client: TestClient):
    resp = client.get("/members")
    assert resp.status_code == 200
    members = resp.json()
    assert len(members) == 3
    you = next(m for m in members if m["id"] == "m-you")
    assert you["isYou"] is True
    assert you["initials"] == "YO"


def test_create_member(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/members", json={"name": "Sam K."}, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Sam K."
    assert body["id"]
    assert body["initials"]
    assert body["isYou"] is False

    members = client.get("/members").json()
    assert len(members) == 4


def test_create_member_requires_name(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/members", json={}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_member_requires_auth(client: TestClient):
    resp = client.post("/members", json={"name": "No auth"})
    assert resp.status_code == 401
