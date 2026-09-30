import anyio

from tekton.composition.worker import run_worker


async def idle_worker(shutdown_requested: anyio.Event) -> None:
    await shutdown_requested.wait()


async def main() -> None:
    await run_worker(idle_worker)


if __name__ == "__main__":
    anyio.run(main)
