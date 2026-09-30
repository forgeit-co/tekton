import signal
import time
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
WORKER_HEARTBEAT_STALE_AFTER_SECONDS = 120
WORKER_HEARTBEAT_INTERVAL_SECONDS = 15
WORKER_HEARTBEAT_PATH = Path("/tmp/tekton-worker-heartbeat")


def worker_heartbeat_is_fresh(heartbeat_path: Path, now: float | None = None) -> bool:
    if not heartbeat_path.is_file():
        return False
    try:
        heartbeat_timestamp = float(heartbeat_path.read_text(encoding="utf-8"))
    except ValueError:
        return False
    current_timestamp = time.time() if now is None else now
    return current_timestamp - heartbeat_timestamp <= WORKER_HEARTBEAT_STALE_AFTER_SECONDS


async def run_worker(
    worker: Worker,
    configuration: RuntimeConfiguration | None = None,
    configuration_path: Path | None = None,
    heartbeat_path: Path = WORKER_HEARTBEAT_PATH,
    heartbeat_interval_seconds: float = WORKER_HEARTBEAT_INTERVAL_SECONDS,
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

    async def publish_heartbeat() -> None:
        while not shutdown_requested.is_set():
            heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
            heartbeat_path.write_text(str(time.time()), encoding="utf-8")
            await anyio.sleep(heartbeat_interval_seconds)

    async def run_and_signal_completion() -> None:
        try:
            await worker(shutdown_requested)
        finally:
            shutdown_requested.set()
            worker_stopped.set()

    async def wait_for_shutdown() -> None:
        with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
            await signals.__anext__()
        shutdown_requested.set()

    try:
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(run_and_signal_completion)
            task_group.start_soon(publish_heartbeat)
            task_group.start_soon(wait_for_shutdown)
            await shutdown_requested.wait()
            with anyio.move_on_after(RUNTIME_DRAIN_TIMEOUT_SECONDS):
                await worker_stopped.wait()
            task_group.cancel_scope.cancel()
    finally:
        heartbeat_path.unlink(missing_ok=True)
        services.engine.dispose()
