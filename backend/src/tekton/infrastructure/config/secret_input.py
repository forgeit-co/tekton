import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from tekton.infrastructure.config.secret import Secret


@dataclass(frozen=True, slots=True)
class SecretInput:
    secrets: dict[str, Secret]

    @classmethod
    def load(cls, secrets_directory: Path) -> SecretInput:
        if not secrets_directory.is_dir():
            return cls(secrets={})

        loaded_secrets: dict[str, Secret] = {}
        for secret_path in sorted(secrets_directory.iterdir()):
            if secret_path.is_file():
                secret_value = secret_path.read_text(encoding="utf-8").strip()
                loaded_secrets[secret_path.name] = Secret(secret_value)
        return cls(secrets=loaded_secrets)

    @classmethod
    def from_document(cls, path: Path) -> SecretInput:
        document: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        schema_version: object = document.get("schema_version")
        if type(schema_version) is not int or schema_version != 1:
            raise ValueError("secret input must use schema_version 1")
        values: object = document.get("secrets")
        if not isinstance(values, dict):
            raise ValueError("secret input must contain a secrets table")

        secret_values = cast("dict[str, object]", values)
        invalid_values = [value for value in secret_values.values() if not isinstance(value, str)]
        if invalid_values:
            raise ValueError("secret input values must be strings")

        return cls(
            secrets={
                name: Secret(value)
                for name, value in secret_values.items()
                if isinstance(value, str)
            }
        )
