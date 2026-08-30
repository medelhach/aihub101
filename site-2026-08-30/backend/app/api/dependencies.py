import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, cast
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.core.container import AppContainer
from app.core.exceptions import InfrastructureError
from app.core.logging import get_logger
from app.database.session import session_scope


def get_container(request: Request) -> AppContainer:
    return cast(AppContainer, request.app.state.container)


def get_request_settings(
    container: Annotated[AppContainer, Depends(get_container)],
) -> Settings:
    return container.settings


def get_request_logger(request: Request) -> logging.LoggerAdapter[logging.Logger]:
    return get_logger(
        "app.request",
        correlation_id=getattr(request.state, "correlation_id", None),
    )


@dataclass(frozen=True, slots=True)
class CurrentUser:
    id: UUID | None = None
    is_authenticated: bool = False


def get_current_user_placeholder() -> CurrentUser:
    """Anonymous principal until the authentication milestone is implemented."""
    return CurrentUser()


async def get_database_session(
    container: Annotated[AppContainer, Depends(get_container)],
) -> AsyncIterator[AsyncSession]:
    if container.session_factory is None:
        raise InfrastructureError("Database is not configured.")

    async for session in session_scope(container.session_factory):
        yield session
