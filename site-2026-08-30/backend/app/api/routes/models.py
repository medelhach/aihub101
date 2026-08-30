from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_database_session
from app.core.exceptions import NotFoundError, ValidationError
from app.modules.catalog.comparison import compare_models
from app.modules.publishing.persistence.repositories import PublishingRepository
from app.schemas.catalog import ComparisonResponse, ModelDetailResponse, ModelSummaryResponse

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[ModelSummaryResponse])
async def list_models(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    provider: str | None = None,
    modality: str | None = None,
    open_weights: bool | None = None,
) -> list[ModelSummaryResponse]:
    models = await PublishingRepository(session).list_models(
        provider=provider, modality=modality, open_weights=open_weights
    )
    return [ModelSummaryResponse.model_validate(model) for model in models]


@router.get("/compare", response_model=ComparisonResponse)
async def compare(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    slugs: Annotated[list[str], Query(min_length=2, max_length=6)],
) -> ComparisonResponse:
    unique = list(dict.fromkeys(slugs))
    if len(unique) < 2:
        raise ValidationError("Select at least two distinct models.")
    models = await PublishingRepository(session).get_models_by_slugs(unique)
    if len(models) != len(unique):
        missing = sorted(set(unique) - {str(model["slug"]) for model in models})
        raise NotFoundError("One or more models were not found.", details={"slugs": missing})
    payload = compare_models(models)
    return ComparisonResponse.model_validate(
        {
            **payload,
            "models": [ModelDetailResponse.model_validate(model) for model in models],
        }
    )


@router.get("/{slug}", response_model=ModelDetailResponse)
async def get_model(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ModelDetailResponse:
    model = await PublishingRepository(session).get_model(slug)
    if model is None:
        raise NotFoundError("Model not found.")
    return ModelDetailResponse.model_validate(model)
