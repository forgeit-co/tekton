from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from tekton.composition.core import compose_core
from tekton.infrastructure.config.bootstrap import (
    BootstrapInputs,
    RuntimeConfiguration,
    load_runtime_configuration,
)
from tekton.infrastructure.database.migrations import SchemaMismatchError
from tekton.presentation.api.openapi import configure_openapi_documentation
from tekton.presentation.api.problem import install_problem_handlers
from tekton.presentation.api.router import register_api_routes


def create_api_app(
    configuration: RuntimeConfiguration | None = None,
    configuration_path: Path | None = None,
    secrets_directory: Path | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        runtime_configuration = configuration
        if runtime_configuration is None:
            environment_inputs = BootstrapInputs.from_environment()
            inputs = BootstrapInputs(
                configuration_path=(configuration_path or environment_inputs.configuration_path),
                secrets_directory=(secrets_directory or environment_inputs.secrets_directory),
            )
            runtime_configuration = load_runtime_configuration(inputs)
        try:
            app.state.services = compose_core(runtime_configuration)
            app.state.health_check = app.state.services.health_check
            yield
        except SchemaMismatchError as error:
            raise RuntimeError(f"startup.schema_mismatch: {error}") from error
        finally:
            services = getattr(app.state, "services", None)
            if services is not None:
                services.engine.dispose()

    app = FastAPI(title="Tekton API", version="0.1.0", lifespan=lifespan)
    register_api_routes(app)
    configure_openapi_documentation(app)
    install_problem_handlers(app)
    return app
