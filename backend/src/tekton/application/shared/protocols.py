from typing import Any, Protocol


class ReadSession(Protocol):
    def execute(self, statement: Any) -> Any: ...


class WriteSession(ReadSession, Protocol):
    def collect_events(self) -> tuple[object, ...]: ...


class Committer(Protocol):
    def commit(self, session: WriteSession) -> None: ...
