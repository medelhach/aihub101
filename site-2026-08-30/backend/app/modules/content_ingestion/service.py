import asyncio
from collections.abc import Iterable
from dataclasses import dataclass

from app.modules.content_ingestion.config import IngestionConfig
from app.modules.content_ingestion.exceptions import ContentValidationError
from app.modules.content_ingestion.interfaces import (
    ContentFetcher,
    ContentNormalizer,
    ContentParser,
    ContentSource,
    ContentValidator,
    DuplicateDetector,
)
from app.modules.content_ingestion.models import DuplicateAssessment, NormalizedContent
from app.modules.content_ingestion.operations import FetchProvenance


class ParserRegistry:
    def __init__(self, parsers: Iterable[ContentParser]) -> None:
        self._parsers: dict[str, ContentParser] = {}
        for parser in parsers:
            if parser.name in self._parsers:
                raise ValueError(f"Duplicate parser registration: {parser.name}")
            self._parsers[parser.name] = parser

    def get(self, name: str) -> ContentParser:
        try:
            return self._parsers[name]
        except KeyError as exc:
            raise ContentValidationError(
                "Source requested an unknown parser.",
                details={"parser": name},
            ) from exc


@dataclass(frozen=True, slots=True)
class IngestionItem:
    content: NormalizedContent
    duplicate: DuplicateAssessment


@dataclass(frozen=True, slots=True)
class IngestionRun:
    source_id: str
    items: tuple[IngestionItem, ...]
    response_etag: str | None = None
    response_last_modified: str | None = None
    not_modified: bool = False
    provenance: tuple[FetchProvenance, ...] = ()


class ContentIngestionEngine:
    def __init__(
        self,
        *,
        config: IngestionConfig,
        fetcher: ContentFetcher,
        parsers: ParserRegistry,
        normalizer: ContentNormalizer,
        validator: ContentValidator,
        duplicate_detector: DuplicateDetector,
    ) -> None:
        self._config = config
        self._fetcher = fetcher
        self._parsers = parsers
        self._normalizer = normalizer
        self._validator = validator
        self._duplicate_detector = duplicate_detector

    async def ingest(self, source: ContentSource) -> IngestionRun:
        descriptor = source.descriptor
        if not self._config.is_source_enabled(descriptor.id):
            return IngestionRun(source_id=descriptor.id, items=())

        parser = self._parsers.get(source.parser_name)
        items: list[IngestionItem] = []
        response_etag: str | None = None
        response_last_modified: str | None = None
        not_modified = False
        provenance: list[FetchProvenance] = []
        for request in await source.build_requests():
            fetched = await self._fetcher.fetch(request)
            provenance.append(
                FetchProvenance(
                    final_url=fetched.final_url,
                    fetched_at=fetched.fetched_at,
                    status_code=fetched.status_code,
                    etag=fetched.etag,
                    last_modified=fetched.last_modified,
                )
            )
            response_etag = fetched.etag or response_etag
            response_last_modified = fetched.last_modified or response_last_modified
            if fetched.not_modified:
                not_modified = True
                continue
            parsed_items = await asyncio.to_thread(parser.parse, fetched)
            for parsed in parsed_items:
                normalized = self._normalizer.normalize(parsed, descriptor)
                self._validator.validate(normalized)
                duplicate = await self._duplicate_detector.assess(normalized)
                items.append(IngestionItem(normalized, duplicate))
        return IngestionRun(
            source_id=descriptor.id,
            items=tuple(items),
            response_etag=response_etag,
            response_last_modified=response_last_modified,
            not_modified=not_modified,
            provenance=tuple(provenance),
        )
