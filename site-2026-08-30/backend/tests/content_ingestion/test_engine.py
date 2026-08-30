from collections.abc import Sequence

import pytest

from app.modules.content_ingestion.config import IngestionConfig
from app.modules.content_ingestion.models import (
    DuplicateAssessment,
    FetchedContent,
    FetchRequest,
    NormalizedContent,
    SourceDescriptor,
)
from app.modules.content_ingestion.normalizer import DefaultContentNormalizer
from app.modules.content_ingestion.parsers.json import JSONContentParser
from app.modules.content_ingestion.service import ContentIngestionEngine, ParserRegistry
from app.modules.content_ingestion.validation import DefaultContentValidator
from tests.content_ingestion.helpers import fetched


class FakeSource:
    descriptor = SourceDescriptor("source", "Source", "generic", "en")
    parser_name = "json"

    async def build_requests(self) -> Sequence[FetchRequest]:
        return [FetchRequest("https://example.com/feed", self.descriptor.id)]


class MockFetcher:
    async def fetch(self, request: FetchRequest) -> FetchedContent:
        return fetched(
            '{"items":[{"title":"Item","url":"https://example.com/item"}]}',
            content_type="application/json",
        )


class MockDuplicateDetector:
    async def assess(self, content: NormalizedContent) -> DuplicateAssessment:
        return DuplicateAssessment(is_duplicate=False)


def engine(config: IngestionConfig | None = None) -> ContentIngestionEngine:
    return ContentIngestionEngine(
        config=config or IngestionConfig(),
        fetcher=MockFetcher(),
        parsers=ParserRegistry([JSONContentParser()]),
        normalizer=DefaultContentNormalizer(),
        validator=DefaultContentValidator(),
        duplicate_detector=MockDuplicateDetector(),
    )


@pytest.mark.asyncio
async def test_engine_composes_generic_pipeline() -> None:
    result = await engine().ingest(FakeSource())
    assert result.source_id == "source"
    assert result.items[0].content.title == "Item"
    assert result.items[0].duplicate.is_duplicate is False


@pytest.mark.asyncio
async def test_disabled_source_is_not_fetched() -> None:
    result = await engine(IngestionConfig(disabled_sources=frozenset({"source"}))).ingest(
        FakeSource()
    )
    assert result.items == ()
