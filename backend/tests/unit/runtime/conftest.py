from pathlib import Path

import pytest
from fastapi import FastAPI

from tekton.composition.control import create_control_app
from tekton.composition.mcp import create_mcp_app
from tekton.infrastructure.config.bootstrap import RuntimeConfiguration
from tekton.infrastructure.config.document import (
    ConfigurationDocument,
    DatabaseSettings,
    ServerSettings,
)
from tekton.infrastructure.config.secret_input import SecretInput


@pytest.fixture
def runtime_configuration(tmp_path: Path) -> RuntimeConfiguration:
    database_path = tmp_path / "unmigrated.sqlite3"
    return RuntimeConfiguration(
        document=ConfigurationDocument(
            schema_version=1,
            server=ServerSettings(),
            database=DatabaseSettings(path=str(database_path)),
        ),
        secrets=SecretInput(secrets={}),
    )


@pytest.fixture
def control_app(runtime_configuration: RuntimeConfiguration) -> FastAPI:
    return create_control_app(configuration=runtime_configuration)


@pytest.fixture
def mcp_app(runtime_configuration: RuntimeConfiguration) -> FastAPI:
    return create_mcp_app(configuration=runtime_configuration)
