from pathlib import Path

from tekton.infrastructure.config.bootstrap import RuntimeConfiguration
from tekton.infrastructure.database.migrations import run_migrations
from tekton.infrastructure.orm.mappers import run_all_mappers


def migrate_database(configuration: RuntimeConfiguration) -> None:
    run_all_mappers()
    run_migrations(configuration.document.database)


def migration_database_path(configuration: RuntimeConfiguration) -> Path:
    return Path(configuration.document.database.path)
