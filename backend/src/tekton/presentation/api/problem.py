from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

PROBLEM_MEDIA_TYPE = "application/problem+json"
HTTP_ERROR_CODES = {
    400: "validation.failed",
    401: "auth.required",
    403: "forbidden",
    404: "not_found",
    405: "method.not_allowed",
    409: "conflict",
    413: "request.too_large",
    415: "media_type.unsupported",
    422: "validation.failed",
    428: "precondition.required",
    500: "internal",
    503: "service.unavailable",
}


def install_problem_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exception: RequestValidationError
    ) -> JSONResponse:
        return _problem_response(
            status=422,
            code="validation.failed",
            title="Request validation failed",
            detail="One or more request fields are invalid.",
            errors=[_validation_error(error) for error in exception.errors()],
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        request: Request, exception: StarletteHTTPException
    ) -> JSONResponse:
        code = HTTP_ERROR_CODES.get(exception.status_code, "http.error")
        return _problem_response(
            status=exception.status_code,
            code=code,
            title="Request failed",
            detail=str(exception.detail),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exception: Exception) -> JSONResponse:
        return _problem_response(
            status=500,
            code="internal",
            title="Internal server error",
            detail="An unexpected error occurred.",
        )


def _validation_error(error: Mapping[str, Any]) -> dict[str, object]:
    location = tuple(error.get("loc", ()))
    location_kind = str(location[0]) if location else "body"
    path = "/" + "/".join(str(part) for part in location[1:])
    return {"in": location_kind, "path": path, "code": "invalid", "params": {}}


def _problem_response(
    status: int,
    code: str,
    title: str,
    detail: str,
    errors: list[dict[str, object]] | None = None,
) -> JSONResponse:
    content: dict[str, object] = {
        "type": f"urn:tekton:error:{code}",
        "title": title,
        "status": status,
        "code": code,
        "detail": detail,
        "params": {},
    }
    if errors is not None:
        content["errors"] = errors
    return JSONResponse(status_code=status, content=content, media_type=PROBLEM_MEDIA_TYPE)
