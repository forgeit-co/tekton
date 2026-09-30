from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class HealthStatus:
    status: str
    schema_revision: str


class HealthReader(Protocol):
    def read_health(self) -> HealthStatus: ...


class HealthCheck:
    def __init__(self, reader: HealthReader):
        self._reader = reader

    def execute(self) -> HealthStatus:
        return self._reader.read_health()
