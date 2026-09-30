import signal
from collections.abc import Awaitable, Callable

import anyio

Worker = Callable[[anyio.Event], Awaitable[None]]
RUNTIME_DRAIN_TIMEOUT_SECONDS = 30


async def run_worker(worker: Worker) -> None:
    shutdown_requested = anyio.Event()
    worker_stopped = anyio.Event()

    async def run_and_signal_completion() -> None:
        await worker(shutdown_requested)
        worker_stopped.set()

    async def wait_for_shutdown() -> None:
        with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
            await signals.__anext__()
        shutdown_requested.set()

    async with anyio.create_task_group() as task_group:
        task_group.start_soon(run_and_signal_completion)
        task_group.start_soon(wait_for_shutdown)
        await shutdown_requested.wait()
        with anyio.move_on_after(RUNTIME_DRAIN_TIMEOUT_SECONDS):
            await worker_stopped.wait()
        task_group.cancel_scope.cancel()
