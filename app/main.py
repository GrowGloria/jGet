from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import (
    admin_jobs,
    auth,
    device_tokens,
    groups,
    lessons,
    managers,
    materials,
    notifications,
    payments,
    students,
)
from app.core.errors import register_exception_handlers
from app.core.logging import RequestLogMiddleware, configure_logging
from app.core.settings import settings
from app.core.trace import TraceIdMiddleware


def create_app() -> FastAPI:
    configure_logging()

    openapi_url = "/openapi.json"
    docs_url = "/docs"
    redoc_url = "/redoc"
    if settings.API_PREFIX:
        openapi_url = f"{settings.API_PREFIX}{openapi_url}"
        docs_url = f"{settings.API_PREFIX}{docs_url}"
        redoc_url = f"{settings.API_PREFIX}{redoc_url}"

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        openapi_url=openapi_url,
        docs_url=docs_url,
        redoc_url=redoc_url,
    )

    app.add_middleware(TraceIdMiddleware)
    app.add_middleware(RequestLogMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(auth.router, prefix=settings.API_PREFIX)
    app.include_router(students.router, prefix=settings.API_PREFIX)
    app.include_router(groups.router, prefix=settings.API_PREFIX)
    app.include_router(lessons.router, prefix=settings.API_PREFIX)
    app.include_router(materials.router, prefix=settings.API_PREFIX)
    app.include_router(notifications.router, prefix=settings.API_PREFIX)
    app.include_router(payments.router, prefix=settings.API_PREFIX)
    app.include_router(device_tokens.router, prefix=settings.API_PREFIX)
    app.include_router(managers.router, prefix=settings.API_PREFIX)
    app.include_router(admin_jobs.router, prefix=settings.API_PREFIX)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
