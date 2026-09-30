from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

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
def migrated_database(tmp_path: Path) -> Iterator[Path]:
    database_path = tmp_path / "tekton.sqlite3"
    database_settings = DatabaseSettings(path=str(database_path))
    run_migrations(database_settings)
    yield database_path


@pytest.fixture
def api_client(migrated_database: Path) -> Iterator[TestClient]:
    configuration = RuntimeConfiguration(
        document=ConfigurationDocument(
            schema_version=1,
            server=ServerSettings(),
            database=DatabaseSettings(path=str(migrated_database)),
        ),
        secrets=SecretInput(secrets={}),
    )
    app = create_api_app(configuration=configuration)
    with TestClient(app) as client:
        yield client
