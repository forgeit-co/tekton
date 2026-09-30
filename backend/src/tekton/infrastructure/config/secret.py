from dataclasses import dataclass

REDACTED_PLACEHOLDER = "<redacted:secret>"


@dataclass(frozen=True, repr=False, slots=True)
class Secret:
    _material: str

    def expose(self) -> str:
        return self._material

    def __repr__(self) -> str:
        return REDACTED_PLACEHOLDER

    def __str__(self) -> str:
        return REDACTED_PLACEHOLDER
