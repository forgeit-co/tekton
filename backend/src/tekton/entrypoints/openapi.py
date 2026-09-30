import json

from tekton.composition.api import create_api_app
from tekton.infrastructure.config.bootstrap import (
    RuntimeConfiguration,
)
from tekton.infrastructure.config.document import (
    ConfigurationDocument,
    DatabaseSettings,
    ServerSettings,
)
from tekton.infrastructure.config.secret_input import SecretInput


def main() -> None:
    configuration = RuntimeConfiguration(
        document=ConfigurationDocument(
            schema_version=1,
            server=ServerSettings(),
            database=DatabaseSettings(path="/tmp/tekton-openapi.sqlite3"),
        ),
        secrets=SecretInput(secrets={}),
    )
    app = create_api_app(configuration=configuration)
    print(json.dumps(app.openapi(), indent=2))


if __name__ == "__main__":
    main()
