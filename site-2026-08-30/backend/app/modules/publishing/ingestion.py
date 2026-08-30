from urllib.parse import urlsplit
from uuid import uuid4

import httpx

from app.config.settings import Settings
from app.core.logging import get_logger
from app.modules.content_ingestion.config import IngestionConfig
from app.modules.content_ingestion.fetchers.http import HttpContentFetcher
from app.modules.content_ingestion.models import DuplicateAssessment, NormalizedContent
from app.modules.content_ingestion.normalizer import DefaultContentNormalizer
from app.modules.content_ingestion.operations import RegisteredSource
from app.modules.content_ingestion.parsers.atom import AtomParser
from app.modules.content_ingestion.parsers.rss import RSSParser
from app.modules.content_ingestion.persistence.uow import PostgreSQLIngestionUnitOfWork
from app.modules.content_ingestion.rate_limit import InMemoryRateLimiter
from app.modules.content_ingestion.rss_source import RSSSource
from app.modules.content_ingestion.runner import SourceAdapterRegistry
from app.modules.content_ingestion.security import SSRFGuard
from app.modules.content_ingestion.service import ContentIngestionEngine, ParserRegistry
from app.modules.content_ingestion.validation import DefaultContentValidator
from app.modules.publishing.atom_source import AtomFeedSource
from app.modules.publishing.sources import FEED_SOURCES


class AcceptAllDuplicateDetector:
    async def assess(self, content: NormalizedContent) -> DuplicateAssessment:
        return DuplicateAssessment(is_duplicate=False)


class LoggingMetrics:
    def __init__(self) -> None:
        self._logger = get_logger("ingestion.metrics")

    def run_started(self, source_key: str) -> None:
        self._logger.info("ingestion_run_started", extra={"source_key": source_key})

    def run_completed(self, source_key: str, status: object, item_count: int) -> None:
        self._logger.info(
            "ingestion_run_completed",
            extra={"source_key": source_key, "status": str(status), "item_count": item_count},
        )

    def run_failed(self, source_key: str, error_code: str) -> None:
        self._logger.warning(
            "ingestion_run_failed", extra={"source_key": source_key, "error_code": error_code}
        )


class LoggingDeadLetterSink:
    def __init__(self) -> None:
        self._logger = get_logger("ingestion.dead_letter")

    async def publish(self, dead_letter: object) -> None:
        self._logger.error("ingestion_dead_letter", extra={"dead_letter": str(dead_letter)})


def build_http_client(settings: Settings, *, follow_redirects: bool) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        follow_redirects=follow_redirects,
        headers={"User-Agent": settings.content_ingestion_user_agent},
        timeout=settings.content_ingestion_timeout_seconds,
    )


def build_engine(settings: Settings, client: httpx.AsyncClient) -> ContentIngestionEngine:
    config = IngestionConfig.from_settings(settings)
    return ContentIngestionEngine(
        config=config,
        fetcher=HttpContentFetcher(
            client,
            config,
            url_guard=SSRFGuard(),
            rate_limiter=InMemoryRateLimiter(config.rate_limit_per_minute),
        ),
        parsers=ParserRegistry([RSSParser(), AtomParser()]),
        normalizer=DefaultContentNormalizer(),
        validator=DefaultContentValidator(),
        duplicate_detector=AcceptAllDuplicateDetector(),
    )


async def ensure_feed_sources(uow: PostgreSQLIngestionUnitOfWork) -> int:
    saved = 0
    for feed in FEED_SOURCES:
        await uow.sources.save(
            RegisteredSource(
                id=uuid4(),
                key=feed.key,
                name=feed.name,
                source_type="rss" if feed.parser_name == "rss" else "atom",
                endpoint_url=feed.endpoint_url,
                parser_name=feed.parser_name,
                content_type=feed.section,
                language=feed.language,
                enabled=True,
                allowed_domains=feed.allowed_domains,
                poll_interval_seconds=feed.poll_interval_seconds,
            )
        )
        saved += 1
    return saved


def source_adapter_registry() -> SourceAdapterRegistry:
    return SourceAdapterRegistry(
        {
            "rss": lambda source, checkpoint: RSSSource(source, checkpoint),
            "atom": lambda source, checkpoint: AtomFeedSource(source, checkpoint),
        }
    )


def article_host_allowlist(url: str, extra: tuple[str, ...]) -> tuple[str, ...]:
    hostname = (urlsplit(url).hostname or "").rstrip(".").casefold()
    hosts = {hostname, *extra}
    return tuple(host for host in hosts if host)
