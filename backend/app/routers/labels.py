from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.deps import get_store
from app.models import Label, LabelCreate, User
from app.store import InMemoryStore

router = APIRouter(tags=["Labels"])


@router.get("/labels", response_model=list[Label])
def list_labels(store: InMemoryStore = Depends(get_store)) -> list[Label]:
    return store.list_labels()


@router.post("/labels", response_model=Label, status_code=201)
def create_label(
    data: LabelCreate,
    store: InMemoryStore = Depends(get_store),
    _: User = Depends(get_current_user),
) -> Label:
    return store.create_label(data)
