from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.deps import get_store
from app.models import Project, ProjectCreate, Task, User
from app.store import InMemoryStore

router = APIRouter(tags=["Projects"])


@router.get("/projects", response_model=list[Project])
def list_projects(store: InMemoryStore = Depends(get_store)) -> list[Project]:
    return store.list_projects()


@router.post("/projects", response_model=Project, status_code=201)
def create_project(
    data: ProjectCreate,
    store: InMemoryStore = Depends(get_store),
    _: User = Depends(get_current_user),
) -> Project:
    return store.create_project(data)


@router.get("/projects/{project_id}/tasks", response_model=list[Task], tags=["Tasks"])
def list_project_tasks(project_id: str, store: InMemoryStore = Depends(get_store)) -> list[Task]:
    return store.list_tasks_by_project(project_id)
