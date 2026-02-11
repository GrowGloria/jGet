import traceback
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.exceptions import HTTPException

from app.core.logging import configure_logging
from app.core.trace import trace_id_ctx


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class BadRequest(AppError):
    def __init__(self, code: str = "BAD_REQUEST", message: str = "Bad request") -> None:
        super().__init__(code, message, status.HTTP_400_BAD_REQUEST)


class Unauthorized(AppError):
    def __init__(self, code: str = "UNAUTHORIZED", message: str = "Unauthorized") -> None:
        super().__init__(code, message, status.HTTP_401_UNAUTHORIZED)


class Forbidden(AppError):
    def __init__(self, code: str = "FORBIDDEN", message: str = "Forbidden") -> None:
        super().__init__(code, message, status.HTTP_403_FORBIDDEN)


class NotFound(AppError):
    def __init__(self, code: str = "NOT_FOUND", message: str = "Not found") -> None:
        super().__init__(code, message, status.HTTP_404_NOT_FOUND)


class Conflict(AppError):
    def __init__(self, code: str = "CONFLICT", message: str = "Conflict") -> None:
        super().__init__(code, message, status.HTTP_409_CONFLICT)


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None) or trace_id_ctx.get()


def error_body(code: str, message: str, trace_id: str | None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "trace_id": trace_id}}


def register_exception_handlers(app: FastAPI) -> None:
    configure_logging()

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        trace_id = _trace_id(request)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(exc.code, exc.message, trace_id),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        trace_id = _trace_id(request)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_body("VALIDATION_ERROR", "Validation error", trace_id),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        trace_id = _trace_id(request)
        code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            code = "UNAUTHORIZED"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            code = "FORBIDDEN"
        elif exc.status_code == status.HTTP_404_NOT_FOUND:
            code = "NOT_FOUND"
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(code, exc.detail, trace_id),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        trace_id = _trace_id(request)
        stack = traceback.format_exc()
        # We intentionally avoid DB logging to keep the schema minimal.
        _ = stack
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_body("INTERNAL_ERROR", "Internal server error", trace_id),
        )
