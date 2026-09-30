import uvicorn

from tekton.composition.control import create_control_app

app = create_control_app()


if __name__ == "__main__":
    uvicorn.run("tekton.entrypoints.control:app", host="127.0.0.1", port=8002)
