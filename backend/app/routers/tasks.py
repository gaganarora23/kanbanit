from fastapi import APIRouter, Depends, Response

from app.auth import get_current_user
from app.deps import get_store
from app.models import Task, TaskCreate, TaskMove, TaskUpdate, User
from app.store import InMemoryStore

router = APIRouter(tags=["Tasks"])


@router.post("/tasks", response_model=Task, status_code=201)
def create_task(
    data: TaskCreate,
    store: InMemoryStore = Depends(get_store),
    _: User = Depends(get_current_user),
) -> Task:
    return store.create_task(data)


@router.patch("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: str,
    data: TaskUpdate,
    store: InMemoryStore = Depends(get_store),
    _: User = Depends(get_current_user),
) -> Task:
    return store.update_task(task_id, data)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    store: InMemoryStore = Depends(get_store),
    _: User = Depends(get_current_user),
) -> Response:
    store.delete_task(task_id)
    return Response(status_code=204)


@router.post("/tasks/{task_id}/move", response_model=Task)
def move_task(
    task_id: str,
    data: TaskMove,
    store: InMemoryStore = Depends(get_store),
    _: User = Depends(get_current_user),
) -> Task:
    return store.move_task(task_id, data)
