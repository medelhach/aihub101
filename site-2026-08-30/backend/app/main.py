from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router
from app.config.settings import Settings, get_settings
from app.core.container import AppContainer
from app.core.error_handlers import register_error_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware


def create_application(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(
        resolved_settings.app_log_level,
        service=resolved_settings.app_name,
        environment=resolved_settings.app_env,
        version=resolved_settings.app_version,
    )
    container = AppContainer.build(resolved_settings)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.container = container
        if container.session_factory is not None:
            from app.modules.publishing.persistence.repositories import PublishingRepository

            async with container.session_factory() as session:
                try:
                    await PublishingRepository(session).seed_models()
                    await session.commit()
                except Exception:
                    await session.rollback()
        yield
        if container.engine is not None:
            await container.engine.dispose()

    application = FastAPI(
        title=resolved_settings.app_name,
        debug=resolved_settings.app_debug,
        version=resolved_settings.app_version,
        docs_url="/docs" if resolved_settings.app_docs_enabled else None,
        redoc_url="/redoc" if resolved_settings.app_docs_enabled else None,
        openapi_url="/openapi.json" if resolved_settings.app_docs_enabled else None,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in resolved_settings.app_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(GZipMiddleware, minimum_size=resolved_settings.app_gzip_minimum_size)
    application.add_middleware(
        TrustedHostMiddleware, allowed_hosts=resolved_settings.app_trusted_hosts
    )
    application.add_middleware(RequestContextMiddleware)
    register_error_handlers(application)
    application.include_router(api_router)
    return application


app = create_application()
