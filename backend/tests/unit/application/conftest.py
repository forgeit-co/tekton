from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from tekton.application.commit.pipeline import CommitPipeline
from tekton.infrastructure.config.document import DatabaseSettings
from tekton.infrastructure.database.sqlite import create_session_factory, create_sqlite_engine
from tekton.infrastructure.shared.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
def unit_of_work_with_pending_write(
    engine_with_commit_table: Engine,
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(create_session_factory(engine_with_commit_table))


@pytest.fixture
def engine_with_commit_table(tmp_path: Path) -> Iterator[Engine]:
    engine = create_sqlite_engine(tmp_path / "commit.sqlite3", DatabaseSettings().sqlite)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE committed_values (value TEXT NOT NULL)"))
    yield engine
    engine.dispose()


@pytest.fixture
def commit_pipeline() -> CommitPipeline:
    return CommitPipeline()
