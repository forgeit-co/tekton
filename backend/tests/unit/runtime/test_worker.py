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
    heartbeat_path = tmp_path / "worker-heartbeat"

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
            await run_worker(
                cooperative_worker,
                configuration=configuration,
                heartbeat_path=heartbeat_path,
                heartbeat_interval_seconds=0.01,
            )

    anyio.run(exercise_worker)

    assert worker_drained.is_set(), "Worker shutdown must wait for in-flight work to drain"
    assert not heartbeat_path.exists(), "Worker shutdown must remove its heartbeat"


def test_worker_publishes_and_refreshes_the_heartbeat(tmp_path: Path):
    heartbeat_path = tmp_path / "worker-heartbeat"
    worker_started = anyio.Event()
    heartbeat_refreshed = anyio.Event()

    async def cooperative_worker(shutdown_requested: anyio.Event) -> None:
        worker_started.set()
        with anyio.fail_after(2):
            while not heartbeat_path.exists():
                await anyio.sleep(0.01)
            first_heartbeat = heartbeat_path.read_text(encoding="utf-8")
            while heartbeat_path.read_text(encoding="utf-8") == first_heartbeat:
                await anyio.sleep(0.01)
        heartbeat_refreshed.set()

    async def send_sigterm_after_heartbeat_refresh() -> None:
        await worker_started.wait()
        await heartbeat_refreshed.wait()
        os.kill(os.getpid(), signal.SIGTERM)

    async def exercise_worker() -> None:
        database_path = tmp_path / "worker-heartbeat-test.sqlite3"
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
            task_group.start_soon(send_sigterm_after_heartbeat_refresh)
            await run_worker(
                cooperative_worker,
                configuration=configuration,
                heartbeat_path=heartbeat_path,
                heartbeat_interval_seconds=0.01,
            )

    anyio.run(exercise_worker)

    assert heartbeat_refreshed.is_set(), "Worker must refresh heartbeat while running"
    assert not heartbeat_path.exists(), "Worker shutdown must remove its heartbeat"
