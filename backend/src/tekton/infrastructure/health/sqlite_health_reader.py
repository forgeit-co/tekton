from sqlalchemy import Engine, text

from tekton.application.health.health import HealthReader, HealthStatus


class SqliteHealthReader(HealthReader):
    def __init__(self, engine: Engine, current_revision: str):
        self._engine = engine
        self._current_revision = current_revision

    def read_health(self) -> HealthStatus:
        with self._engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return HealthStatus(status="ok", schema_revision=self._current_revision)
