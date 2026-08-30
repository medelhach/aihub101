from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.dependencies import get_container, get_request_settings
from app.config.settings import Settings
from app.core.container import AppContainer
from app.core.exceptions import InfrastructureError, ValidationError
from app.modules.publishing.service import ContentCycleService
from app.schemas.catalog import CycleResponse

router = APIRouter(prefix="/operations", tags=["operations"])


@router.post("/content-cycle", response_model=CycleResponse)
async def run_content_cycle(
    settings: Annotated[Settings, Depends(get_request_settings)],
    container: Annotated[AppContainer, Depends(get_container)],
    x_content_cycle_key: Annotated[str | None, Header()] = None,
) -> CycleResponse:
    expected = (
        settings.content_cycle_secret.get_secret_value() if settings.content_cycle_secret else None
    )
    if expected and x_content_cycle_key != expected:
        raise ValidationError("Invalid content cycle key.")
    if container.session_factory is None:
        raise InfrastructureError("Database is not configured.")
    factory: async_sessionmaker[AsyncSession] = container.session_factory
    result = await ContentCycleService(settings, factory).run()
    return CycleResponse(
        sources_processed=result.sources_processed,
        candidates_created=result.candidates_created,
        stories_published=result.stories_published,
        stories_skipped=result.stories_skipped,
        models_seeded=result.models_seeded,
        details=result.details,
    )
