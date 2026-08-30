from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import get_container
from app.core.container import AppContainer
from app.core.logging import get_logger
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])
DatabaseStatus = Literal["connected", "disconnected", "not_configured"]
logger = get_logger(__name__)


async def _database_status(container: AppContainer) -> DatabaseStatus:
    if container.engine is None:
        return "not_configured"
    try:
        async with container.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return "connected"
    except SQLAlchemyError:
        logger.warning("database_health_check_failed", exc_info=True)
        return "disconnected"


@router.get("", response_model=HealthResponse, summary="Check API availability")
async def health_check(
    container: Annotated[AppContainer, Depends(get_container)],
) -> HealthResponse:
    database = await _database_status(container)
    return HealthResponse(
        status="healthy" if database == "connected" else "degraded",
        service=container.settings.app_name,
        version=container.settings.app_version,
        environment=container.settings.app_env,
        database=database,
    )


@router.get("/live", response_model=HealthResponse, summary="Check process liveness")
async def liveness(
    container: Annotated[AppContainer, Depends(get_container)],
) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=container.settings.app_name,
        version=container.settings.app_version,
        environment=container.settings.app_env,
        database="not_configured",
    )


@router.get("/ready", response_model=HealthResponse, summary="Check application readiness")
async def readiness(
    response: Response,
    container: Annotated[AppContainer, Depends(get_container)],
) -> HealthResponse:
    database = await _database_status(container)
    ready = database == "connected"
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status="healthy" if ready else "unhealthy",
        service=container.settings.app_name,
        version=container.settings.app_version,
        environment=container.settings.app_env,
        database=database,
    )
