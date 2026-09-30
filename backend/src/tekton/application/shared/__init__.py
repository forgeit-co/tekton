from typing import Protocol


class Actor(Protocol):
    author_kind: str
    author_id: str
    causation_id: str
