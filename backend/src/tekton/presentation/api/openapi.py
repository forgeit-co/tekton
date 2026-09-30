from typing import Any

from fastapi import FastAPI

OpenApiSchema = dict[str, Any]


def configure_openapi_documentation(app: FastAPI) -> None:
    original_openapi = app.openapi

    def openapi_with_validation_removed() -> OpenApiSchema:
        if app.openapi_schema:
            return app.openapi_schema
        schema = original_openapi()
        schema.get("components", {}).get("schemas", {}).pop("HTTPValidationError", None)
        schema.get("components", {}).get("schemas", {}).pop("ValidationError", None)
        app.openapi_schema = schema
        return schema

    app.openapi = openapi_with_validation_removed
