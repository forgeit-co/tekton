import signal
from collections.abc import Awaitable, Callable
from pathlib import Path

import anyio

from tekton.composition.core import compose_core
from tekton.infrastructure.config.bootstrap import (
    BootstrapInputs,
    RuntimeConfiguration,
    load_runtime_configuration,
)
from tekton.infrastructure.database.migrations import SchemaMismatchError

Worker = Callable[[anyio.Event], Awaitable[None]]
RUNTIME_DRAIN_TIMEOUT_SECONDS = 30


async def run_worker(
    worker: Worker,
    configuration: RuntimeConfiguration | None = None,
    configuration_path: Path | None = None,
) -> None:
    runtime_configuration = configuration
    if runtime_configuration is None:
        environment_inputs = BootstrapInputs.from_environment()
        inputs = BootstrapInputs(
            configuration_path=configuration_path or environment_inputs.configuration_path,
            secrets_directory=environment_inputs.secrets_directory,
        )
        runtime_configuration = load_runtime_configuration(inputs)

    try:
        services = compose_core(runtime_configuration)
    except SchemaMismatchError as error:
        raise RuntimeError(f"startup.schema_mismatch: {error}") from error

    shutdown_requested = anyio.Event()
    worker_stopped = anyio.Event()

    async def run_and_signal_completion() -> None:
        try:
            await worker(shutdown_requested)
        finally:
            worker_stopped.set()

    async def wait_for_shutdown() -> None:
        with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
            await signals.__anext__()
        shutdown_requested.set()

    try:
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(run_and_signal_completion)
            task_group.start_soon(wait_for_shutdown)
            await shutdown_requested.wait()
            with anyio.move_on_after(RUNTIME_DRAIN_TIMEOUT_SECONDS):
                await worker_stopped.wait()
            task_group.cancel_scope.cancel()
    finally:
        services.engine.dispose()
