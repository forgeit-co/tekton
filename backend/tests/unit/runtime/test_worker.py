import os
import signal

import anyio

from tekton.composition.worker import run_worker


def test_worker_receives_sigterm_and_drains_before_exit():
    worker_started = anyio.Event()
    worker_drained = anyio.Event()

    async def cooperative_worker(shutdown_requested: anyio.Event) -> None:
        worker_started.set()
        await shutdown_requested.wait()
        worker_drained.set()

    async def send_sigterm() -> None:
        await worker_started.wait()
        os.kill(os.getpid(), signal.SIGTERM)

    async def exercise_worker() -> None:
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(send_sigterm)
            await run_worker(cooperative_worker)

    anyio.run(exercise_worker)

    assert worker_drained.is_set(), "Worker shutdown must wait for in-flight work to drain"
