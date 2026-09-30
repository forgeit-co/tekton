from typing import Any, Self

from sqlalchemy import Executable
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker

from tekton.application.shared.protocols import WriteSession
from tekton.infrastructure.config.sqlite import SQLiteTransactionKind
from tekton.infrastructure.database.sqlite import begin_transaction


class SqlAlchemyUnitOfWork(WriteSession):
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        transaction_kind: SQLiteTransactionKind = SQLiteTransactionKind.WRITE,
    ):
        self._session_factory = session_factory
        self._transaction_kind: SQLiteTransactionKind = transaction_kind
        self._session: Session | None = None
        self._events: list[object] = []

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        begin_transaction(self._session.connection(), self._transaction_kind)
        return self

    def __exit__(self, exception_type: object, exception_value: object, traceback: object) -> None:
        if self._session is not None:
            self._session.rollback()
            self._session.close()
            self._session = None

    def execute(self, statement: Executable) -> Result[Any]:
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._session.execute(statement)

    def collect_events(self) -> tuple[object, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        self._session.commit()

    def rollback(self) -> None:
        if self._session is not None:
            self._session.rollback()
