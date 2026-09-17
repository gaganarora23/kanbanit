from fastapi.testclient import TestClient


def test_list_labels_returns_seed_data(client: TestClient):
    resp = client.get("/labels")
    assert resp.status_code == 200
    labels = resp.json()
    assert len(labels) == 8
    names = {l["name"] for l in labels}
    assert names == {"Bug", "Feature", "Research", "Content", "Mobile", "API", "Ideas", "Shipped"}


def test_create_label(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/labels", json={"name": "Design", "color": "#abcdef"}, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Design"
    assert body["color"] == "#abcdef"
    assert body["id"]

    labels = client.get("/labels").json()
    assert len(labels) == 9


def test_create_label_requires_fields(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/labels", json={"name": "No color"}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_label_requires_auth(client: TestClient):
    resp = client.post("/labels", json={"name": "No auth", "color": "#000000"})
    assert resp.status_code == 401
