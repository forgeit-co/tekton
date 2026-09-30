from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from tekton.infrastructure.config.document import DatabaseSettings
from tekton.infrastructure.database.migrations import MigrationIntegrityError, run_migrations


def test_migration_integrity_failure_rolls_back_database_changes(
    database_with_foreign_key_violation: Engine,
):
    database_path = Path(str(database_with_foreign_key_violation.url.database))

    with pytest.raises(MigrationIntegrityError, match="foreign_key_check"):
        run_migrations(DatabaseSettings(path=str(database_path)))

    with database_with_foreign_key_violation.connect() as connection:
        revision_table_exists = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        ).scalar_one_or_none()
        rows = connection.execute(text("SELECT parent_id, value FROM child")).all()

    assert revision_table_exists is None, "Failed migration must roll back the version marker"
    assert rows == [(42, "old")], "Failed migration must preserve pre-existing database rows"
