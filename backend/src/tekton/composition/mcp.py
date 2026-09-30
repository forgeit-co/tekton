from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from tekton.composition.core import compose_core
from tekton.infrastructure.config.bootstrap import (
    BootstrapInputs,
    RuntimeConfiguration,
    load_runtime_configuration,
)
from tekton.infrastructure.database.migrations import SchemaMismatchError


def create_mcp_app(
    configuration: RuntimeConfiguration | None = None,
    configuration_path: Path | None = None,
    database_path: Path | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        runtime_configuration = configuration
        if runtime_configuration is None:
            environment_inputs = BootstrapInputs.from_environment()
            inputs = BootstrapInputs(
                configuration_path=configuration_path or environment_inputs.configuration_path,
                secrets_directory=environment_inputs.secrets_directory,
            )
            runtime_configuration = load_runtime_configuration(inputs)
        if database_path is not None:
            runtime_configuration = RuntimeConfiguration(
                document=runtime_configuration.document.with_database_path(database_path),
                secrets=runtime_configuration.secrets,
            )
        try:
            app.state.services = compose_core(runtime_configuration)
            yield
        except SchemaMismatchError as error:
            raise RuntimeError(f"startup.schema_mismatch: {error}") from error
        finally:
            services = getattr(app.state, "services", None)
            if services is not None:
                services.engine.dispose()

    app = FastAPI(
        title="Tekton MCP", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan
    )
    app.add_api_route(
        "/health/live",
        lambda: PlainTextResponse("ok", media_type="text/plain"),
        methods=["GET"],
        response_class=PlainTextResponse,
        operation_id="getMcpHealthLive",
    )
    return app
