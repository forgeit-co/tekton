from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...


class StepRevalidator(Protocol):
    def revalidate(self, step_id: str) -> bool: ...


class CompletionBlockerSource(Protocol):
    def blockers(self) -> tuple[str, ...]: ...


class ApprovalHandler(Protocol):
    def handle(self, approval_id: str) -> bool: ...


class AwaitedItemResolver(Protocol):
    def resolve(self, item_id: str) -> bool: ...


class RunFinalizationPort(Protocol):
    def finalize(self, run_id: str) -> bool: ...


class RunSuspender(Protocol):
    def suspend(self, run_id: str) -> bool: ...
