from fastapi.testclient import TestClient


def test_create_task_minimal(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post(
        "/tasks",
        json={"projectId": "p-atlas", "title": "New task", "status": "todo"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "New task"
    assert body["projectId"] == "p-atlas"
    assert body["status"] == "todo"
    assert body["priority"] is None
    assert body["labelIds"] == []
    assert body["assigneeId"] is None
    assert body["id"]
    assert body["createdAt"]

    tasks = client.get("/projects/p-atlas/tasks").json()
    assert any(t["id"] == body["id"] for t in tasks)


def test_create_task_full(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post(
        "/tasks",
        json={
            "projectId": "p-atlas",
            "title": "Full task",
            "description": "Details here",
            "status": "in_progress",
            "priority": "P1",
            "labelIds": ["l-bug"],
            "assigneeId": "m-you",
            "due": "Fri",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["description"] == "Details here"
    assert body["priority"] == "P1"
    assert body["labelIds"] == ["l-bug"]
    assert body["assigneeId"] == "m-you"
    assert body["due"] == "Fri"


def test_create_task_appends_to_end_of_column(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post(
        "/tasks",
        json={"projectId": "p-atlas", "title": "Last in parked", "status": "parked"},
        headers=auth_headers,
    )
    new_id = resp.json()["id"]
    tasks = client.get("/projects/p-atlas/tasks").json()
    parked_ids = [t["id"] for t in tasks if t["status"] == "parked"]
    assert parked_ids == ["t-1", "t-2", "t-3", new_id]


def test_create_task_missing_required_field(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/tasks", json={"projectId": "p-atlas", "status": "todo"}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_task_invalid_status(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post(
        "/tasks",
        json={"projectId": "p-atlas", "title": "Bad status", "status": "bogus"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_task_invalid_priority(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post(
        "/tasks",
        json={"projectId": "p-atlas", "title": "Bad priority", "status": "todo", "priority": "P9"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_task_unknown_project_returns_404(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post(
        "/tasks",
        json={"projectId": "does-not-exist", "title": "Orphan", "status": "todo"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_create_task_requires_auth(client: TestClient):
    resp = client.post("/tasks", json={"projectId": "p-atlas", "title": "No auth", "status": "todo"})
    assert resp.status_code == 401


def test_update_task_partial_fields(client: TestClient, auth_headers: dict[str, str]):
    resp = client.patch("/tasks/t-1", json={"title": "Renamed", "priority": "P1"}, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Renamed"
    assert body["priority"] == "P1"
    # untouched fields survive
    assert body["projectId"] == "p-atlas"
    assert body["labelIds"] == ["l-research"]


def test_update_task_can_clear_optional_fields(client: TestClient, auth_headers: dict[str, str]):
    resp = client.patch("/tasks/t-1", json={"assigneeId": None, "priority": None}, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["assigneeId"] is None
    assert body["priority"] is None


def test_update_task_not_found_returns_404(client: TestClient, auth_headers: dict[str, str]):
    resp = client.patch("/tasks/does-not-exist", json={"title": "x"}, headers=auth_headers)
    assert resp.status_code == 404


def test_update_task_status_moves_it_to_end_of_new_column(client: TestClient, auth_headers: dict[str, str]):
    resp = client.patch("/tasks/t-1", json={"status": "complete"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "complete"

    tasks = client.get("/projects/p-atlas/tasks").json()
    parked_ids = [t["id"] for t in tasks if t["status"] == "parked"]
    complete_ids = [t["id"] for t in tasks if t["status"] == "complete"]
    assert "t-1" not in parked_ids
    assert complete_ids == ["t-9", "t-10", "t-1"]


def test_update_task_requires_auth(client: TestClient):
    resp = client.patch("/tasks/t-1", json={"title": "No auth"})
    assert resp.status_code == 401


def test_delete_task(client: TestClient, auth_headers: dict[str, str]):
    resp = client.delete("/tasks/t-1", headers=auth_headers)
    assert resp.status_code == 204

    tasks = client.get("/projects/p-atlas/tasks").json()
    assert all(t["id"] != "t-1" for t in tasks)


def test_delete_task_not_found_returns_404(client: TestClient, auth_headers: dict[str, str]):
    resp = client.delete("/tasks/does-not-exist", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_task_twice_returns_404_second_time(client: TestClient, auth_headers: dict[str, str]):
    assert client.delete("/tasks/t-1", headers=auth_headers).status_code == 204
    assert client.delete("/tasks/t-1", headers=auth_headers).status_code == 404


def test_delete_task_requires_auth(client: TestClient):
    resp = client.delete("/tasks/t-1")
    assert resp.status_code == 401
