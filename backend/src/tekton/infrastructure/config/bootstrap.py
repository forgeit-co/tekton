import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from tekton.infrastructure.config.document import ConfigurationDocument
from tekton.infrastructure.config.secret_input import SecretInput

DEFAULT_CONFIGURATION_PATH = Path("deploy/backend.toml")
DEFAULT_SECRETS_DIRECTORY = Path("deploy/secrets")


@dataclass(frozen=True, slots=True)
class BootstrapInputs:
    configuration_path: Path
    secrets_directory: Path

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] = os.environ) -> BootstrapInputs:
        configuration_path = Path(
            environment.get("TEKTON_CONFIGURATION_PATH", DEFAULT_CONFIGURATION_PATH)
        )
        secrets_directory = Path(
            environment.get("TEKTON_SECRETS_DIRECTORY", DEFAULT_SECRETS_DIRECTORY)
        )
        return cls(configuration_path=configuration_path, secrets_directory=secrets_directory)


@dataclass(frozen=True, slots=True)
class RuntimeConfiguration:
    document: ConfigurationDocument
    secrets: SecretInput


def load_runtime_configuration(inputs: BootstrapInputs) -> RuntimeConfiguration:
    return RuntimeConfiguration(
        document=ConfigurationDocument.load(inputs.configuration_path),
        secrets=SecretInput.load(inputs.secrets_directory),
    )
