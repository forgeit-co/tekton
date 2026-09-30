from fastapi import FastAPI

from tekton.presentation.api.health.router import router as health_router


def register_api_routes(app: FastAPI) -> None:
    app.include_router(health_router)
