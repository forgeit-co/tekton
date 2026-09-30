from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI

from tekton.composition.api import create_api_app
from tekton.infrastructure.config.bootstrap import RuntimeConfiguration
from tekton.infrastructure.config.document import (
    ConfigurationDocument,
    DatabaseSettings,
    ServerSettings,
)
from tekton.infrastructure.config.secret_input import SecretInput
from tekton.infrastructure.database.migrations import run_migrations
from tests.api.client import ApiClient


@pytest.fixture
def migrated_database(tmp_path: Path) -> Iterator[Path]:
    database_path = tmp_path / "tekton.sqlite3"
    database_settings = DatabaseSettings(path=str(database_path))
    run_migrations(database_settings)
    yield database_path


@pytest.fixture
def api_app(migrated_database: Path) -> FastAPI:
    configuration = RuntimeConfiguration(
        document=ConfigurationDocument(
            schema_version=1,
            server=ServerSettings(),
            database=DatabaseSettings(path=str(migrated_database)),
        ),
        secrets=SecretInput(secrets={}),
    )
    return create_api_app(configuration=configuration)


@pytest.fixture
def api_client(api_app: FastAPI) -> Iterator[ApiClient]:
    with ApiClient(api_app) as client:
        yield client
