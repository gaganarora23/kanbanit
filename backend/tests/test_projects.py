from fastapi.testclient import TestClient


def test_list_projects_returns_seed_data(client: TestClient):
    resp = client.get("/projects")
    assert resp.status_code == 200
    projects = resp.json()
    assert len(projects) == 4
    ids = {p["id"] for p in projects}
    assert ids == {"p-atlas", "p-mobile", "p-design", "p-marketing"}
    atlas = next(p for p in projects if p["id"] == "p-atlas")
    assert atlas["name"] == "Atlas Redesign"
    assert atlas["color"] == "#2f5bff"


def test_create_project(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/projects", json={"name": "New Initiative", "color": "#123456"}, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "New Initiative"
    assert body["color"] == "#123456"
    assert body["id"]

    listed = client.get("/projects").json()
    assert len(listed) == 5
    assert any(p["id"] == body["id"] for p in listed)


def test_create_project_requires_fields(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/projects", json={"name": "Missing color"}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_project_requires_auth(client: TestClient):
    resp = client.post("/projects", json={"name": "No auth", "color": "#000000"})
    assert resp.status_code == 401


def test_list_project_tasks_returns_tasks_grouped_by_column_order(client: TestClient):
    resp = client.get("/projects/p-atlas/tasks")
    assert resp.status_code == 200
    tasks = resp.json()
    assert [t["id"] for t in tasks] == [
        "t-1", "t-2", "t-3",  # parked
        "t-4", "t-5", "t-6",  # todo
        "t-7", "t-8",         # in_progress
        "t-9", "t-10",        # complete
    ]
    assert all(t["projectId"] == "p-atlas" for t in tasks)


def test_list_project_tasks_scoped_to_project(client: TestClient):
    resp = client.get("/projects/p-mobile/tasks")
    assert resp.status_code == 200
    ids = {t["id"] for t in resp.json()}
    assert ids == {"t-11", "t-12"}


def test_list_tasks_for_unknown_project_returns_404(client: TestClient):
    resp = client.get("/projects/does-not-exist/tasks")
    assert resp.status_code == 404
