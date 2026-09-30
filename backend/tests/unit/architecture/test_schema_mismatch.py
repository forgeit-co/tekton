from pathlib import Path

import pytest

from tekton.infrastructure.config.document import DatabaseSettings
from tekton.infrastructure.database.migrations import SchemaMismatchError, require_current_schema
from tekton.infrastructure.database.sqlite import create_sqlite_engine


def test_backend_schema_preflight_rejects_database_without_current_revision(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "unmigrated.sqlite3", DatabaseSettings().sqlite)

    with pytest.raises(SchemaMismatchError, match="startup.schema_mismatch"):
        require_current_schema(engine)

    engine.dispose()


def test_backend_schema_preflight_rejects_database_behind_migration_head(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "old-schema.sqlite3", DatabaseSettings().sqlite)

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"
        )
        connection.exec_driver_sql("INSERT INTO alembic_version (version_num) VALUES ('old')")

    with pytest.raises(SchemaMismatchError, match="startup.schema_mismatch"):
        require_current_schema(engine)

    engine.dispose()
