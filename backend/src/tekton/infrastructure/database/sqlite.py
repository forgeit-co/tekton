import sqlite3
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session, sessionmaker

from tekton.infrastructure.config.sqlite import SQLiteSettings, SQLiteTransactionKind


def create_sqlite_engine(database_path: Path, settings: SQLiteSettings | None = None) -> Engine:
    sqlite_settings = settings or SQLiteSettings()
    if str(database_path) != ":memory:":
        database_path.parent.mkdir(parents=True, exist_ok=True)
    if str(database_path) == ":memory:":
        sqlite_url = "sqlite:///:memory:"
    else:
        sqlite_url = f"sqlite:///{database_path}"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False, "isolation_level": None},
    )

    @event.listens_for(engine, "connect")
    def configure_sqlite_connection(
        connection: sqlite3.Connection, connection_record: object
    ) -> None:
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA journal_mode={sqlite_settings.journal_mode}")
        cursor.execute(f"PRAGMA busy_timeout={sqlite_settings.busy_timeout_ms}")
        cursor.execute(f"PRAGMA synchronous={sqlite_settings.synchronous}")
        foreign_keys_enabled = "ON" if sqlite_settings.foreign_keys else "OFF"
        cursor.execute(f"PRAGMA foreign_keys={foreign_keys_enabled}")
        cursor.close()

    return engine


def begin_transaction(connection: Connection, transaction_kind: SQLiteTransactionKind) -> None:
    match transaction_kind:
        case SQLiteTransactionKind.READ:
            connection.exec_driver_sql("BEGIN DEFERRED")
        case SQLiteTransactionKind.WRITE:
            connection.exec_driver_sql("BEGIN IMMEDIATE")


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
