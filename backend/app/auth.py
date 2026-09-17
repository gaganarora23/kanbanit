"""Password hashing, opaque bearer tokens, and the auth dependency routes use to require one.

Uses bcrypt directly for hashing (no plaintext password is ever stored or returned) and a
random opaque token per login, mapped to a user id in the store. No JWT — the token is just a
lookup key into InMemoryStore's token table, which is enough for this mock-backend phase.
"""

from __future__ import annotations

import secrets

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Read the store directly off app state (rather than via app.deps.get_store) to avoid a
    # module-import cycle: store.py imports hash_password/generate_token from this module.
    store = request.app.state.store
    user = store.get_user_by_token(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
