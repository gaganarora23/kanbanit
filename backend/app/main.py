from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import auth, labels, members, projects, tasks
from app.store import InMemoryStore, NotFoundError

DEV_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5183",
    "http://localhost:5184",
    "http://localhost:4173",
]


def create_app() -> FastAPI:
    app = FastAPI(title="Kanvas Kanban API", version="1.0.0")
    app.state.store = InMemoryStore()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=DEV_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    app.include_router(auth.router)
    app.include_router(projects.router)
    app.include_router(tasks.router)
    app.include_router(labels.router)
    app.include_router(members.router)

    return app


app = create_app()
