import contextvars
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

trace_id_ctx = contextvars.ContextVar("trace_id", default=None)


def generate_trace_id() -> str:
    return uuid.uuid4().hex


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id") or generate_trace_id()
        token = trace_id_ctx.set(trace_id)
        request.state.trace_id = trace_id
        try:
            response: Response = await call_next(request)
        finally:
            trace_id_ctx.reset(token)
        response.headers["X-Trace-Id"] = trace_id
        return response
