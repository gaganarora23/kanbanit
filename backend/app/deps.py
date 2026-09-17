from fastapi import Request

from app.store import InMemoryStore


def get_store(request: Request) -> InMemoryStore:
    return request.app.state.store
