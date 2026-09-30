from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from tekton.presentation.api.health.models import HealthOut

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health/live", response_class=PlainTextResponse, operation_id="getHealthLive")
def get_health_live() -> PlainTextResponse:
    return PlainTextResponse("ok", media_type="text/plain")


@router.get("/health", response_model=HealthOut, operation_id="getHealth")
def get_health(request: Request) -> HealthOut:
    health_check = request.app.state.health_check
    health = health_check.execute()
    return HealthOut(status=health.status, schema_revision=health.schema_revision)
