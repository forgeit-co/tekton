from pathlib import Path

from sqlalchemy import text

from tekton.infrastructure.config.document import DatabaseSettings
from tekton.infrastructure.database.sqlite import create_session_factory, create_sqlite_engine
from tekton.infrastructure.shared.unit_of_work import SqlAlchemyUnitOfWork


def test_unit_of_work_rolls_back_when_commit_is_not_called(tmp_path: Path):
    engine = create_sqlite_engine(tmp_path / "uow.sqlite3", DatabaseSettings().sqlite)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE sample (value INTEGER)"))
    session_factory = create_session_factory(engine)

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        unit_of_work.execute(text("INSERT INTO sample (value) VALUES (1)"))

    with engine.connect() as connection:
        rows = connection.execute(text("SELECT value FROM sample")).all()

    engine.dispose()
    assert rows == [], "Uncommitted unit-of-work changes must roll back"
