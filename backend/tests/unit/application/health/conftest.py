from pathlib import Path

import anyio
import pytest

from tekton.application.health.health import HealthCheck
from tekton.composition.api import create_api_app
from tekton.infrastructure.config.bootstrap import RuntimeConfiguration
from tekton.infrastructure.config.document import (
    ConfigurationDocument,
    DatabaseSettings,
    ServerSettings,
)
from tekton.infrastructure.config.secret_input import SecretInput
from tekton.infrastructure.database.migrations import run_migrations


@pytest.fixture
def two_started_api_apps(tmp_path: Path) -> tuple[HealthCheck, HealthCheck]:
    database_path = tmp_path / "meta.sqlite3"
    run_migrations(DatabaseSettings(path=str(database_path)))
    configuration = RuntimeConfiguration(
        document=ConfigurationDocument(
            schema_version=1,
            server=ServerSettings(),
            database=DatabaseSettings(path=str(database_path)),
        ),
        secrets=SecretInput(secrets={}),
    )
    first_app = create_api_app(configuration=configuration)
    second_app = create_api_app(configuration=configuration)
    first_health_check: HealthCheck | None = None
    second_health_check: HealthCheck | None = None

    async def start_apps() -> None:
        nonlocal first_health_check, second_health_check
        async with first_app.router.lifespan_context(first_app):
            first_health_check = first_app.state.health_check
            async with second_app.router.lifespan_context(second_app):
                second_health_check = second_app.state.health_check

    anyio.run(start_apps)
    if first_health_check is None or second_health_check is None:
        raise AssertionError("Both API app lifespans must compose health services")
    return first_health_check, second_health_check
