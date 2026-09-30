import uvicorn

from tekton.composition.mcp import create_mcp_app

app = create_mcp_app()


if __name__ == "__main__":
    uvicorn.run("tekton.entrypoints.mcp:app", host="127.0.0.1", port=8001)
