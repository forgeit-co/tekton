from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


def create_mcp_app() -> FastAPI:
    app = FastAPI(title="Tekton MCP", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_api_route(
        "/health/live",
        lambda: PlainTextResponse("ok", media_type="text/plain"),
        methods=["GET"],
        response_class=PlainTextResponse,
        operation_id="getMcpHealthLive",
    )
    return app
