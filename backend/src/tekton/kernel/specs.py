from typing import Protocol


class DecisionSpec(Protocol):
    key: str


class DerivedSpec(Protocol):
    key: str


class Check(Protocol):
    key: str


class CheckResult(Protocol):
    result: str


class Node(Protocol):
    kind: str
    key: str
