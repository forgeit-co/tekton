from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class SQLiteSettings:
    busy_timeout_ms: int = 5000
    foreign_keys: bool = True
    synchronous: str = "NORMAL"
    journal_mode: str = "WAL"


class SQLiteTransactionKind(StrEnum):
    READ = "read"
    WRITE = "write"
