from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient


class ApiClient(TestClient):
    app: FastAPI

    def get(self, url: str | object, **kwargs: Any) -> Any:
        parent_get = cast("Any", super().get)
        return parent_get(url, **kwargs)
