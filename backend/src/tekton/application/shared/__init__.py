from typing import Protocol


class WriteSession(Protocol):
    def collect_events(self) -> tuple[object, ...]: ...


class ReadSession(Protocol):
    pass


class Committer(Protocol):
    def commit(self) -> bool: ...


class Actor(Protocol):
    author_kind: str
    author_id: str
    causation_id: str
