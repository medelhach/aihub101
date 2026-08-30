from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.schemas.errors import ProblemDetail

logger = get_logger(__name__)


def _response(
    *,
    status_code: int,
    code: str,
    title: str,
    message: str,
    request: Request,
    details: dict[str, Any] | list[dict[str, Any]] | None = None,
) -> JSONResponse:
    body = ProblemDetail(
        type=f"/problems/{code}",
        title=title,
        status=status_code,
        detail=message,
        instance=request.url.path,
        code=code,
        correlation_id=getattr(request.state, "correlation_id", None),
        errors=details,
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json"),
        media_type="application/problem+json",
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("application_error", extra={"error_code": exc.code})
    return _response(
        status_code=exc.status_code,
        code=exc.code,
        title=exc.code.replace("_", " ").title(),
        message=exc.message,
        request=request,
        details=exc.details,
    )


async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return _response(
        status_code=422,
        code="request_validation_error",
        title="Request Validation Error",
        message="Request validation failed.",
        request=request,
        details=cast(list[dict[str, Any]], jsonable_encoder(exc.errors())),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "HTTP request failed."
    return _response(
        status_code=exc.status_code,
        code="http_error",
        title="HTTP Error",
        message=message,
        request=request,
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception")
    return _response(
        status_code=500,
        code="internal_server_error",
        title="Internal Server Error",
        message="An unexpected error occurred.",
        request=request,
    )


def register_error_handlers(application: FastAPI) -> None:
    application.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    application.add_exception_handler(RequestValidationError, request_validation_handler)  # type: ignore[arg-type]
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    application.add_exception_handler(Exception, unhandled_error_handler)
