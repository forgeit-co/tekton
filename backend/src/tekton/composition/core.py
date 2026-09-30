from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from tekton.application.commit.pipeline import CommitPipeline
from tekton.application.health.health import HealthCheck
from tekton.infrastructure.config.bootstrap import RuntimeConfiguration
from tekton.infrastructure.database.migrations import require_current_schema
from tekton.infrastructure.database.sqlite import create_session_factory, create_sqlite_engine
from tekton.infrastructure.health.sqlite_health_reader import SqliteHealthReader
from tekton.infrastructure.orm.mappers import run_all_mappers
from tekton.infrastructure.shared.unit_of_work import SqlAlchemyUnitOfWork


@dataclass(frozen=True, slots=True)
class CoreServices:
    engine: Engine
    session_factory: sessionmaker[Session]
    unit_of_work_factory: Callable[[], SqlAlchemyUnitOfWork]
    committer: CommitPipeline
    health_check: HealthCheck


def compose_core(configuration: RuntimeConfiguration) -> CoreServices:
    run_all_mappers()
    database_settings = configuration.document.database
    engine = create_sqlite_engine(Path(database_settings.path), database_settings.sqlite)
    revision = require_current_schema(engine)
    session_factory = create_session_factory(engine)
    return CoreServices(
        engine=engine,
        session_factory=session_factory,
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(session_factory),
        committer=CommitPipeline(),
        health_check=HealthCheck(SqliteHealthReader(engine, revision)),
    )
