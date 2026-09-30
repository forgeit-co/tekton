from tekton.composition.migrate import migrate_database
from tekton.infrastructure.config.bootstrap import BootstrapInputs, load_runtime_configuration


def main() -> None:
    configuration = load_runtime_configuration(BootstrapInputs.from_environment())
    migrate_database(configuration)


if __name__ == "__main__":
    main()
