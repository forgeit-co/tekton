from typing import Any, Protocol


class ReadSession(Protocol):
    def execute(self, statement: Any) -> Any: ...


class WriteSession(ReadSession, Protocol):
    def collect_events(self) -> tuple[object, ...]: ...


class CommitCapability(Protocol):
    def commit(self) -> None: ...


class Committer(Protocol):
    def commit(self, session: WriteSession, commit_capability: CommitCapability) -> None: ...
