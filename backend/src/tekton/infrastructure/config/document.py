import dataclasses
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from tekton.infrastructure.config.sqlite import SQLiteSettings

SUPPORTED_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class ServerSettings:
    host: str = "127.0.0.1"
    port: int = 8000


@dataclass(frozen=True, slots=True)
class DatabaseSettings:
    path: str = "data/db/tekton.sqlite3"
    busy_timeout_ms: int = 5000
    foreign_keys: bool = True
    synchronous: str = "NORMAL"
    journal_mode: str = "WAL"

    @property
    def sqlite(self) -> SQLiteSettings:
        return SQLiteSettings(
            busy_timeout_ms=self.busy_timeout_ms,
            foreign_keys=self.foreign_keys,
            synchronous=self.synchronous,
            journal_mode=self.journal_mode,
        )


@dataclass(frozen=True, slots=True)
class ConfigurationDocument:
    schema_version: int
    server: ServerSettings
    database: DatabaseSettings

    @classmethod
    def load(cls, path: Path) -> ConfigurationDocument:
        document: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
        schema_version = document.get("schema_version")
        if type(schema_version) is not int or schema_version != SUPPORTED_SCHEMA_VERSION:
            raise ValueError(
                f"configuration error at schema_version: unsupported version {schema_version!r}"
            )

        known_sections = {"schema_version", "server", "database"}
        unexpected_sections = sorted(set(document) - known_sections)
        if unexpected_sections:
            unknown_section = unexpected_sections[0]
            raise ValueError(f"configuration error at {unknown_section}: unknown table or key")

        server = _section_settings(document, "server", ServerSettings)
        database = _section_settings(document, "database", DatabaseSettings)
        return cls(schema_version=schema_version, server=server, database=database)


def _section_settings[SettingsType](
    document: dict[str, Any], section_name: str, settings_type: type[SettingsType]
) -> SettingsType:
    section: object = document.get(section_name, {})
    if not isinstance(section, dict):
        raise ValueError(f"configuration error at {section_name}: expected a table")

    try:
        settings = settings_type(**cast("dict[str, Any]", section))
    except TypeError as error:
        raise ValueError(f"configuration error at {section_name}: {error}") from error

    if not dataclasses.is_dataclass(settings) or isinstance(settings, type):
        raise ValueError(f"configuration error at {section_name}: expected typed settings")

    for setting in dataclasses.fields(settings):
        expected_type = setting.type
        value: object = getattr(settings, setting.name)
        setting_path = f"{section_name}.{setting.name}"
        if not isinstance(expected_type, type):
            raise ValueError(f"configuration error at {setting_path}: invalid annotation")
        boolean_where_integer_expected = expected_type is int and isinstance(value, bool)
        if boolean_where_integer_expected or not isinstance(value, expected_type):
            raise ValueError(
                f"configuration error at {setting_path}: expected {expected_type.__name__}"
            )

    return settings
