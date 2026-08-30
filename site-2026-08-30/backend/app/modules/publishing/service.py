from datetime import date
from hashlib import sha256
from urllib.parse import urlsplit

import httpx
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config.settings import Settings
from app.core.logging import get_logger
from app.modules.content_ingestion.persistence.uow import PostgreSQLIngestionUnitOfWork
from app.modules.content_ingestion.runner import IngestionRunner
from app.modules.content_ingestion.security import SSRFGuard
from app.modules.publishing.composer import compose_story
from app.modules.publishing.domain import CycleResult, PendingCandidate
from app.modules.publishing.extraction import extract_paragraphs
from app.modules.publishing.ingestion import (
    LoggingDeadLetterSink,
    LoggingMetrics,
    article_host_allowlist,
    build_engine,
    build_http_client,
    ensure_feed_sources,
    source_adapter_registry,
)
from app.modules.publishing.persistence.repositories import PublishingRepository
from app.modules.publishing.rewriter import AzureEditorialRewriter
from app.utils.datetime import utc_now

_AI_TERMS = (
    "ai",
    "artificial intelligence",
    "machine learning",
    "llm",
    "gpt",
    "claude",
    "gemini",
    "openai",
    "anthropic",
    "deepmind",
    "neural",
    "model",
    "chatbot",
    "generative",
    "diffusion",
    "transformer",
    "agent",
    "copilot",
    "foundation model",
)

_BROAD_SOURCES = {"the-verge", "ars-technica", "ieee-spectrum"}


def _looks_like_ai(candidate: PendingCandidate) -> bool:
    if candidate.source_key not in _BROAD_SOURCES:
        return True
    haystack = f"{candidate.title} {candidate.summary or ''}".casefold()
    return any(term in haystack for term in _AI_TERMS)


class ContentCycleService:
    def __init__(
        self,
        settings: Settings,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._settings = settings
        self._session_factory = session_factory
        self._logger = get_logger("publishing.cycle")

    async def run(self) -> CycleResult:
        sources_processed = 0
        candidates_created = 0
        async with PostgreSQLIngestionUnitOfWork(self._session_factory) as uow:
            await ensure_feed_sources(uow)
        async with build_http_client(self._settings, follow_redirects=False) as client:
            engine = build_engine(self._settings, client)
            day = date.today().isoformat()
            async with PostgreSQLIngestionUnitOfWork(self._session_factory) as listing:
                enabled = list(await listing.sources.list_enabled())
            for source in enabled:
                sources_processed += 1
                key = f"{source.key}:{day}:{utc_now().hour}"
                try:
                    async with PostgreSQLIngestionUnitOfWork(self._session_factory) as uow:
                        runner = IngestionRunner(
                            sources=uow.sources,
                            operations=uow.operations,
                            adapters=source_adapter_registry(),
                            engine=engine,
                            metrics=LoggingMetrics(),
                            dead_letters=LoggingDeadLetterSink(),
                            logger=self._logger,
                        )
                        result = await runner.run(source.key, sha256(key.encode()).hexdigest())
                        candidates_created += result.item_count
                except Exception:
                    self._logger.exception("source_cycle_failed", extra={"source_key": source.key})
        published, skipped, models_seeded = await self._publish_pending()
        return CycleResult(
            sources_processed=sources_processed,
            candidates_created=candidates_created,
            stories_published=published,
            stories_skipped=skipped,
            models_seeded=models_seeded,
            details={"hour_bucket": f"{day}:{utc_now().hour}"},
        )

    async def _publish_pending(self) -> tuple[int, int, int]:
        published = 0
        skipped = 0
        async with self._session_factory() as session:
            repo = PublishingRepository(session)
            models_seeded = await repo.seed_models()
            pending = await repo.list_pending_candidates(
                self._settings.publishing_max_candidates_per_cycle
            )
            async with build_http_client(self._settings, follow_redirects=True) as client:
                rewriter = AzureEditorialRewriter(self._settings, client)
                for candidate in pending:
                    try:
                        did_publish = await self._publish_one(repo, client, rewriter, candidate)
                    except Exception:
                        self._logger.exception(
                            "candidate_publish_failed", extra={"candidate_id": str(candidate.id)}
                        )
                        await repo.mark_candidate(candidate.id, "failed")
                        skipped += 1
                        continue
                    if did_publish:
                        published += 1
                    else:
                        skipped += 1
            await session.commit()
        return published, skipped, models_seeded

    async def _publish_one(
        self,
        repo: PublishingRepository,
        client: httpx.AsyncClient,
        rewriter: AzureEditorialRewriter,
        candidate: PendingCandidate,
    ) -> bool:
        canonical = candidate.canonical_url or candidate.url
        if await repo.exists_by_canonical_url(canonical) or not _looks_like_ai(candidate):
            await repo.mark_candidate(candidate.id, "skipped")
            return False
        paragraphs = await self._extract_source(client, candidate)
        composed = compose_story(
            title=candidate.title,
            summary=candidate.summary,
            source_name=candidate.source_name,
            source_url=candidate.url,
            published_at=candidate.published_at,
            author=candidate.author,
            paragraphs=paragraphs,
            tags=candidate.tags,
            section=candidate.section,
        )
        composed = await rewriter.rewrite(candidate, paragraphs, composed)
        story = await repo.save_story(
            candidate=candidate,
            composed=composed,
            published_at=candidate.published_at,
        )
        await repo.mark_candidate(candidate.id, "published" if story else "skipped")
        return story is not None

    async def _extract_source(
        self,
        client: httpx.AsyncClient,
        candidate: PendingCandidate,
    ) -> tuple[str, ...]:
        allowlist = article_host_allowlist(candidate.url, candidate.allowed_domains)
        try:
            await SSRFGuard().validate(candidate.url, allowlist)
            response = await client.get(candidate.url)
            response.raise_for_status()
            host = urlsplit(str(response.url)).hostname or ""
            allowed = {item.casefold() for item in allowlist}
            host_name = host.rstrip(".").casefold()
            if host_name not in allowed and not any(
                host_name.endswith(f".{item}") for item in allowlist
            ):
                return tuple(filter(None, (candidate.summary,)))
            paragraphs = extract_paragraphs(response.text)
            if paragraphs:
                return paragraphs
        except Exception:
            self._logger.info("article_extraction_fallback", extra={"url": candidate.url})
        return tuple(filter(None, (candidate.summary,)))
