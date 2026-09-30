import uvicorn

from tekton.composition.api import create_api_app

app = create_api_app()


if __name__ == "__main__":
    uvicorn.run("tekton.entrypoints.api:app", host="127.0.0.1", port=8000)
