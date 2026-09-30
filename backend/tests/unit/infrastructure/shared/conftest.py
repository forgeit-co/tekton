from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from tekton.infrastructure.config.document import DatabaseSettings
from tekton.infrastructure.database.sqlite import create_sqlite_engine


@pytest.fixture
def database_with_foreign_key_violation(tmp_path: Path) -> Iterator[Engine]:
    engine = create_sqlite_engine(tmp_path / "invalid.sqlite3", DatabaseSettings().sqlite)
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
        connection.execute(text("CREATE TABLE parent (id INTEGER PRIMARY KEY)"))
        connection.execute(
            text(
                "CREATE TABLE child (parent_id INTEGER REFERENCES parent(id), value TEXT NOT NULL)"
            )
        )
        connection.execute(text("INSERT INTO child (parent_id, value) VALUES (42, 'old')"))
        connection.commit()
    yield engine
    engine.dispose()
