from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text

from tekton.infrastructure.config.document import DatabaseSettings
from tekton.infrastructure.database.sqlite import create_sqlite_engine

MIGRATIONS_DIRECTORY = Path(__file__).resolve().parents[4] / "migrations"


class SchemaMismatchError(RuntimeError):
    def __init__(self, current_revision: str | None, head_revision: str | None):
        super().__init__(
            "startup.schema_mismatch: "
            f"database revision {current_revision!r} does not match "
            f"migration head {head_revision!r}"
        )
        self.current_revision = current_revision
        self.head_revision = head_revision


class MigrationIntegrityError(RuntimeError):
    pass


def migration_config() -> Config:
    configuration = Config()
    configuration.set_main_option("script_location", str(MIGRATIONS_DIRECTORY))
    return configuration


def migration_head() -> str | None:
    return ScriptDirectory.from_config(migration_config()).get_current_head()


def current_schema_revision(engine: Engine) -> str | None:
    with engine.connect() as connection:
        return MigrationContext.configure(connection).get_current_revision()


def run_migrations(database_settings: DatabaseSettings) -> None:
    database_path = Path(database_settings.path)
    engine = create_sqlite_engine(database_path, database_settings.sqlite)
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
            connection.commit()
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            transaction = connection.get_transaction()
            if transaction is None:
                raise RuntimeError("Migration transaction did not start")
            try:
                configuration = migration_config()
                configuration.attributes["connection"] = connection
                command.upgrade(configuration, "head")
                violations = connection.execute(text("PRAGMA foreign_key_check")).all()
                if violations:
                    raise MigrationIntegrityError(
                        f"foreign_key_check found {len(violations)} violation(s)"
                    )
                transaction.commit()
            except Exception:
                transaction.rollback()
                raise
            finally:
                connection.rollback()
                connection.exec_driver_sql("PRAGMA foreign_keys=ON")
                connection.commit()
    finally:
        engine.dispose()


def require_current_schema(engine: Engine) -> str:
    current_revision = current_schema_revision(engine)
    head_revision = migration_head()
    if not current_revision or current_revision != head_revision:
        raise SchemaMismatchError(current_revision, head_revision)
    return current_revision
