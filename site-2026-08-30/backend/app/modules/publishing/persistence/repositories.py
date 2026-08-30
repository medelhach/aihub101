from collections.abc import Sequence
from datetime import datetime
from hashlib import sha1
from re import sub
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalog.records import model_catalog
from app.modules.content_ingestion.persistence.models import (
    IngestionCandidateModel,
    IngestionSourceModel,
)
from app.modules.publishing.domain import ComposedStory, PendingCandidate, PublishedStory
from app.modules.publishing.persistence.models import AIModelRecordModel, PublishedStoryModel


def story_slug(headline: str, canonical_url: str) -> str:
    base = sub(r"[^a-z0-9]+", "-", headline.casefold()).strip("-")[:80]
    digest = sha1(canonical_url.encode()).hexdigest()[:8]
    return f"{base}-{digest}" if base else digest


def _story(model: PublishedStoryModel) -> PublishedStory:
    return PublishedStory(
        id=model.id,
        slug=model.slug,
        section=model.section,
        headline=model.headline,
        dek=model.dek,
        dateline=model.dateline,
        lead=model.lead,
        sections=tuple(model.sections),
        key_facts=tuple(model.key_facts),
        entities=tuple(model.entities),
        body_markdown=model.body_markdown,
        tags=tuple(model.tags),
        source_name=model.source_name,
        source_url=model.source_url,
        canonical_url=model.canonical_url,
        author=model.author,
        published_at=model.published_at,
        word_count=model.word_count,
        language=model.language,
        hero_image_url=model.hero_image_url,
        generation_method=model.generation_method,
        created_at=model.created_at,
    )


class PublishingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_pending_candidates(self, limit: int) -> Sequence[PendingCandidate]:
        statement: Select[tuple[IngestionCandidateModel, IngestionSourceModel]] = (
            select(IngestionCandidateModel, IngestionSourceModel)
            .join(
                IngestionSourceModel,
                IngestionCandidateModel.source_id == IngestionSourceModel.id,
            )
            .where(IngestionCandidateModel.status == "pending")
            .order_by(IngestionCandidateModel.created_at.desc())
            .limit(limit)
        )
        rows = await self._session.execute(statement)
        candidates: list[PendingCandidate] = []
        for candidate, source in rows.all():
            section = "articles" if source.content_type == "articles" else "news"
            candidates.append(
                PendingCandidate(
                    id=candidate.id,
                    source_id=source.id,
                    source_key=source.key,
                    source_name=source.name,
                    section=section,
                    title=candidate.title,
                    summary=candidate.summary,
                    published_at=candidate.published_at,
                    author=candidate.author,
                    url=candidate.url,
                    canonical_url=candidate.canonical_url,
                    tags=tuple(candidate.tags),
                    images=tuple(candidate.images),
                    language=candidate.language,
                    allowed_domains=tuple(source.allowed_domains),
                )
            )
        return tuple(candidates)

    async def mark_candidate(self, candidate_id: UUID, status: str) -> None:
        model = await self._session.get(IngestionCandidateModel, candidate_id)
        if model is not None:
            model.status = status

    async def exists_by_canonical_url(self, canonical_url: str) -> bool:
        found = await self._session.scalar(
            select(PublishedStoryModel.id).where(PublishedStoryModel.canonical_url == canonical_url)
        )
        return found is not None

    async def save_story(
        self,
        *,
        candidate: PendingCandidate,
        composed: ComposedStory,
        published_at: datetime | None,
        link_candidate: bool = True,
    ) -> PublishedStory | None:
        canonical = candidate.canonical_url or candidate.url
        statement = insert(PublishedStoryModel).values(
            slug=story_slug(composed.headline, canonical),
            section=candidate.section,
            headline=composed.headline,
            dek=composed.dek,
            dateline=composed.dateline,
            lead=composed.lead,
            sections=[{"heading": item.heading, "body": item.body} for item in composed.sections],
            key_facts=list(composed.key_facts),
            entities=list(composed.entities),
            body_markdown=composed.body_markdown,
            tags=list(composed.tags),
            source_name=candidate.source_name,
            source_url=candidate.url,
            canonical_url=canonical,
            author=candidate.author,
            published_at=published_at,
            word_count=composed.word_count,
            language=candidate.language,
            hero_image_url=candidate.images[0] if candidate.images else None,
            generation_method=composed.generation_method,
            candidate_id=candidate.id if link_candidate else None,
        )
        model = await self._session.scalar(
            statement.on_conflict_do_nothing(constraint="uq_published_stories_canonical_url").returning(
                PublishedStoryModel
            )
        )
        if model is None:
            return None
        return _story(model)

    async def list_stories(
        self,
        section: str,
        *,
        limit: int,
        cursor: datetime | None,
    ) -> tuple[list[PublishedStory], bool]:
        statement = (
            select(PublishedStoryModel)
            .where(PublishedStoryModel.section == section)
            .order_by(
                PublishedStoryModel.published_at.desc().nullslast(),
                PublishedStoryModel.created_at.desc(),
            )
            .limit(limit + 1)
        )
        if cursor is not None:
            statement = statement.where(PublishedStoryModel.published_at < cursor)
        models = list(await self._session.scalars(statement))
        has_more = len(models) > limit
        return [_story(model) for model in models[:limit]], has_more

    async def get_story(self, section: str, slug: str) -> PublishedStory | None:
        model = await self._session.scalar(
            select(PublishedStoryModel).where(
                PublishedStoryModel.section == section,
                PublishedStoryModel.slug == slug,
            )
        )
        return _story(model) if model else None

    async def count_stories(self, section: str) -> int:
        result = await self._session.scalar(
            select(func.count())
            .select_from(PublishedStoryModel)
            .where(PublishedStoryModel.section == section)
        )
        return int(result or 0)

    async def seed_editorial_stories(self) -> int:
        from app.modules.publishing.seed_stories import (
            compose_seed_story,
            editorial_seed_candidates,
        )

        inserted = 0
        for candidate, paragraphs in editorial_seed_candidates():
            if await self.exists_by_canonical_url(candidate.url):
                continue
            composed = compose_seed_story(candidate, paragraphs)
            story = await self.save_story(
                candidate=candidate,
                composed=composed,
                published_at=candidate.published_at,
                link_candidate=False,
            )
            if story is not None:
                inserted += 1
        return inserted

    async def list_models(
        self,
        *,
        provider: str | None = None,
        modality: str | None = None,
        open_weights: bool | None = None,
    ) -> list[dict[str, Any]]:
        statement = select(AIModelRecordModel).order_by(
            AIModelRecordModel.provider, AIModelRecordModel.name
        )
        if provider:
            statement = statement.where(AIModelRecordModel.provider == provider)
        if modality:
            statement = statement.where(AIModelRecordModel.modality == modality)
        if open_weights is not None:
            statement = statement.where(AIModelRecordModel.open_weights.is_(open_weights))
        models = await self._session.scalars(statement)
        return [self._model_payload(model) for model in models]

    async def get_model(self, slug: str) -> dict[str, Any] | None:
        model = await self._session.scalar(
            select(AIModelRecordModel).where(AIModelRecordModel.slug == slug)
        )
        return self._model_payload(model) if model else None

    async def get_models_by_slugs(self, slugs: Sequence[str]) -> list[dict[str, Any]]:
        if not slugs:
            return []
        models = await self._session.scalars(
            select(AIModelRecordModel).where(AIModelRecordModel.slug.in_(list(slugs)))
        )
        by_slug = {model.slug: self._model_payload(model) for model in models}
        return [by_slug[slug] for slug in slugs if slug in by_slug]

    async def seed_models(self) -> int:
        records = list(model_catalog())
        inserted = 0
        for record in records:
            statement = insert(AIModelRecordModel).values(**record)
            update_fields = {
                column.name: getattr(statement.excluded, column.name)
                for column in AIModelRecordModel.__table__.columns
                if column.name not in {"id", "slug", "created_at"}
            }
            result = await self._session.scalar(
                statement.on_conflict_do_update(
                    index_elements=[AIModelRecordModel.slug],
                    set_=update_fields,
                ).returning(AIModelRecordModel.id)
            )
            if result is not None:
                inserted += 1
        return inserted

    @staticmethod
    def _model_payload(model: AIModelRecordModel) -> dict[str, Any]:
        return {
            "id": str(model.id),
            "slug": model.slug,
            "name": model.name,
            "provider": model.provider,
            "family": model.family,
            "release_date": model.release_date,
            "modality": model.modality,
            "context_window_tokens": model.context_window_tokens,
            "max_output_tokens": model.max_output_tokens,
            "parameters": model.parameters,
            "license_name": model.license_name,
            "open_weights": model.open_weights,
            "availability": model.availability,
            "input_price_per_million_usd": model.input_price_per_million_usd,
            "output_price_per_million_usd": model.output_price_per_million_usd,
            "reasoning": model.reasoning,
            "multimodal": model.multimodal,
            "fine_tune_available": model.fine_tune_available,
            "knowledge_cutoff": model.knowledge_cutoff,
            "architecture": model.architecture,
            "deployment_options": model.deployment_options,
            "typical_use_cases": model.typical_use_cases,
            "strengths": model.strengths,
            "limitations": model.limitations,
            "safety_notes": model.safety_notes,
            "documentation_url": model.documentation_url,
            "benchmarks": model.benchmarks,
            "pricing_notes": model.pricing_notes,
        }
