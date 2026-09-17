from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import hash_password, verify_password
from app.deps import get_store
from app.models import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from app.store import InMemoryStore

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserPublic, status_code=201)
def register(data: RegisterRequest, store: InMemoryStore = Depends(get_store)) -> UserPublic:
    if store.get_user_by_username(data.username) is not None:
        raise HTTPException(status_code=400, detail="username already registered")
    user = store.create_user(data.username, hash_password(data.password))
    return UserPublic(id=user.id, username=user.username)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, store: InMemoryStore = Depends(get_store)) -> TokenResponse:
    user = store.get_user_by_username(data.username)
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")
    token = store.create_token(user.id)
    return TokenResponse(access_token=token)
