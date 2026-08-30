from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_database_session
from app.core.exceptions import NotFoundError
from app.modules.publishing.domain import PublishedStory
from app.modules.publishing.persistence.repositories import PublishingRepository
from app.schemas.catalog import StoryDetailResponse, StorySectionResponse, StorySummaryResponse
from app.schemas.common import PageResponse
from app.utils.pagination import decode_cursor, encode_cursor
from app.utils.responses import page_response

router = APIRouter(tags=["publishing"])


def _summary(story: PublishedStory) -> StorySummaryResponse:
    return StorySummaryResponse(
        slug=story.slug,
        section=story.section,
        headline=story.headline,
        dek=story.dek,
        dateline=story.dateline,
        source_name=story.source_name,
        source_url=story.source_url,
        author=story.author,
        published_at=story.published_at,
        word_count=story.word_count,
        tags=list(story.tags),
        hero_image_url=story.hero_image_url,
        generation_method=story.generation_method,
    )


def _detail(story: PublishedStory) -> StoryDetailResponse:
    return StoryDetailResponse(
        **_summary(story).model_dump(),
        lead=story.lead,
        sections=[StorySectionResponse(**section) for section in story.sections],
        key_facts=list(story.key_facts),
        entities=list(story.entities),
        body_markdown=story.body_markdown,
        canonical_url=story.canonical_url,
        language=story.language,
    )


async def _list_stories(
    session: AsyncSession,
    section: str,
    limit: int,
    cursor: str | None,
) -> PageResponse[StorySummaryResponse]:
    repo = PublishingRepository(session)
    decoded = datetime.fromisoformat(decode_cursor(cursor)) if cursor else None
    items, has_more = await repo.list_stories(section, limit=limit, cursor=decoded)
    next_cursor = None
    if has_more and items and items[-1].published_at is not None:
        next_cursor = encode_cursor(items[-1].published_at.isoformat())
    return page_response(
        [_summary(item) for item in items],
        next_cursor=next_cursor,
        has_more=has_more,
        count=await repo.count_stories(section),
    )


@router.get("/news", response_model=PageResponse[StorySummaryResponse])
async def list_news(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    cursor: str | None = None,
) -> PageResponse[StorySummaryResponse]:
    return await _list_stories(session, "news", limit, cursor)


@router.get("/news/{slug}", response_model=StoryDetailResponse)
async def get_news(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> StoryDetailResponse:
    story = await PublishingRepository(session).get_story("news", slug)
    if story is None:
        raise NotFoundError("News story not found.")
    return _detail(story)


@router.get("/articles", response_model=PageResponse[StorySummaryResponse])
async def list_articles(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    cursor: str | None = None,
) -> PageResponse[StorySummaryResponse]:
    return await _list_stories(session, "articles", limit, cursor)


@router.get("/articles/{slug}", response_model=StoryDetailResponse)
async def get_article(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> StoryDetailResponse:
    story = await PublishingRepository(session).get_story("articles", slug)
    if story is None:
        raise NotFoundError("Article not found.")
    return _detail(story)
