from fastapi.testclient import TestClient


def _ids_by_status(client: TestClient, project_id: str, status: str) -> list[str]:
    tasks = client.get(f"/projects/{project_id}/tasks").json()
    return [t["id"] for t in tasks if t["status"] == status]


def test_move_task_to_new_column_appends_by_default(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/tasks/t-1/move", json={"status": "todo"}, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "todo"

    assert _ids_by_status(client, "p-atlas", "parked") == ["t-2", "t-3"]
    assert _ids_by_status(client, "p-atlas", "todo") == ["t-4", "t-5", "t-6", "t-1"]


def test_move_task_with_before_task_id_inserts_at_position(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/tasks/t-1/move", json={"status": "todo", "beforeTaskId": "t-5"}, headers=auth_headers)
    assert resp.status_code == 200

    assert _ids_by_status(client, "p-atlas", "parked") == ["t-2", "t-3"]
    assert _ids_by_status(client, "p-atlas", "todo") == ["t-4", "t-1", "t-5", "t-6"]


def test_move_task_reorder_within_same_column(client: TestClient, auth_headers: dict[str, str]):
    # Move t-6 to the front of todo (before t-4), staying within the todo column.
    resp = client.post("/tasks/t-6/move", json={"status": "todo", "beforeTaskId": "t-4"}, headers=auth_headers)
    assert resp.status_code == 200

    assert _ids_by_status(client, "p-atlas", "todo") == ["t-6", "t-4", "t-5"]


def test_move_task_to_front_of_empty_column(client: TestClient, auth_headers: dict[str, str]):
    # p-mobile has no "in_progress" tasks yet.
    resp = client.post("/tasks/t-11/move", json={"status": "in_progress"}, headers=auth_headers)
    assert resp.status_code == 200

    assert _ids_by_status(client, "p-mobile", "in_progress") == ["t-11"]
    assert _ids_by_status(client, "p-mobile", "todo") == []


def test_move_task_not_found_returns_404(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/tasks/does-not-exist/move", json={"status": "todo"}, headers=auth_headers)
    assert resp.status_code == 404


def test_move_task_before_unknown_task_returns_404(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post(
        "/tasks/t-1/move", json={"status": "todo", "beforeTaskId": "does-not-exist"}, headers=auth_headers
    )
    assert resp.status_code == 404


def test_move_task_before_task_in_different_project_returns_404(client: TestClient, auth_headers: dict[str, str]):
    # t-11 belongs to p-mobile, t-1 belongs to p-atlas.
    resp = client.post("/tasks/t-1/move", json={"status": "todo", "beforeTaskId": "t-11"}, headers=auth_headers)
    assert resp.status_code == 404


def test_move_task_invalid_status_returns_422(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/tasks/t-1/move", json={"status": "bogus"}, headers=auth_headers)
    assert resp.status_code == 422


def test_move_task_requires_auth(client: TestClient):
    resp = client.post("/tasks/t-1/move", json={"status": "todo"})
    assert resp.status_code == 401
