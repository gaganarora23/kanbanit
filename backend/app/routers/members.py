from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.deps import get_store
from app.models import Member, MemberCreate, User
from app.store import InMemoryStore

router = APIRouter(tags=["Members"])


@router.get("/members", response_model=list[Member])
def list_members(store: InMemoryStore = Depends(get_store)) -> list[Member]:
    return store.list_members()


@router.post("/members", response_model=Member, status_code=201)
def create_member(
    data: MemberCreate,
    store: InMemoryStore = Depends(get_store),
    _: User = Depends(get_current_user),
) -> Member:
    return store.create_member(data)
