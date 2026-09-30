import os
import signal
from pathlib import Path

import anyio

from tekton.composition.worker import run_worker
from tekton.infrastructure.config.bootstrap import RuntimeConfiguration
from tekton.infrastructure.config.document import (
    ConfigurationDocument,
    DatabaseSettings,
    ServerSettings,
)
from tekton.infrastructure.config.secret_input import SecretInput
from tekton.infrastructure.database.migrations import run_migrations


def test_worker_lifespan_receives_sigterm_and_drains_before_exit(tmp_path: Path):
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
        database_path = tmp_path / "worker-test.sqlite3"
        run_migrations(DatabaseSettings(path=str(database_path)))
        configuration = RuntimeConfiguration(
            document=ConfigurationDocument(
                schema_version=1,
                server=ServerSettings(),
                database=DatabaseSettings(path=str(database_path)),
            ),
            secrets=SecretInput(secrets={}),
        )
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(send_sigterm)
            await run_worker(cooperative_worker, configuration=configuration)

    anyio.run(exercise_worker)

    assert worker_drained.is_set(), "Worker shutdown must wait for in-flight work to drain"
