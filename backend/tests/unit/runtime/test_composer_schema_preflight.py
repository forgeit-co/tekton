import anyio
import pytest
from fastapi import FastAPI

from tekton.composition.worker import run_worker
from tekton.infrastructure.config.bootstrap import RuntimeConfiguration


def test_control_composer_rejects_a_schema_mismatch(control_app: FastAPI):
    async def start_control_app() -> None:
        async with control_app.router.lifespan_context(control_app):
            raise AssertionError("Control startup accepted an unmigrated database")

    with pytest.raises(RuntimeError, match="startup.schema_mismatch"):
        anyio.run(start_control_app)


def test_mcp_composer_rejects_a_schema_mismatch(mcp_app: FastAPI):
    async def start_mcp_app() -> None:
        async with mcp_app.router.lifespan_context(mcp_app):
            raise AssertionError("MCP startup accepted an unmigrated database")

    with pytest.raises(RuntimeError, match="startup.schema_mismatch"):
        anyio.run(start_mcp_app)


def test_worker_composer_rejects_a_schema_mismatch(runtime_configuration: RuntimeConfiguration):
    async def worker_that_must_not_start(shutdown_requested: anyio.Event) -> None:
        raise AssertionError("Worker startup accepted an unmigrated database")

    async def start_worker() -> None:
        await run_worker(worker_that_must_not_start, configuration=runtime_configuration)

    with pytest.raises(RuntimeError, match="startup.schema_mismatch"):
        anyio.run(start_worker)
