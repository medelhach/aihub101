import httpx
import pytest

from app.modules.content_ingestion.config import IngestionConfig
from app.modules.content_ingestion.exceptions import ContentTooLargeError
from app.modules.content_ingestion.fetchers.http import HttpContentFetcher
from app.modules.content_ingestion.models import FetchRequest


class MockRateLimiter:
    def __init__(self) -> None:
        self.sources: list[str] = []

    async def acquire(self, source_id: str) -> None:
        self.sources.append(source_id)


class MockURLGuard:
    async def validate(self, url: str, allowed_domains: tuple[str, ...]) -> None:
        return None


@pytest.mark.asyncio
async def test_fetcher_downloads_without_parsing() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=b"raw-content", request=request)
    )
    limiter = MockRateLimiter()
    async with httpx.AsyncClient(transport=transport) as client:
        result = await HttpContentFetcher(
            client,
            IngestionConfig(),
            url_guard=MockURLGuard(),
            rate_limiter=limiter,
        ).fetch(FetchRequest("https://example.com/feed", "source"))
    assert result.body == b"raw-content"
    assert result.final_url == "https://example.com/feed"
    assert limiter.sources == ["source"]


@pytest.mark.asyncio
async def test_fetcher_retries_transient_status() -> None:
    attempts = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(503 if attempts == 1 else 200, content=b"ok", request=request)

    async def no_sleep(delay: float) -> None:
        delays.append(delay)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        fetcher = HttpContentFetcher(
            client,
            IngestionConfig(retries=1),
            url_guard=MockURLGuard(),
            sleep=no_sleep,
        )
        result = await fetcher.fetch(FetchRequest("https://example.com/feed", "source"))
    assert result.body == b"ok"
    assert attempts == 2
    assert delays == [1.0]


@pytest.mark.asyncio
async def test_fetcher_rejects_oversized_content() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=b"x" * 1025, request=request)
    )
    async with httpx.AsyncClient(transport=transport) as client:
        fetcher = HttpContentFetcher(
            client,
            IngestionConfig(maximum_article_size_bytes=1024),
            url_guard=MockURLGuard(),
        )
        with pytest.raises(ContentTooLargeError):
            await fetcher.fetch(FetchRequest("https://example.com/feed", "source"))


@pytest.mark.asyncio
async def test_fetcher_returns_conditional_not_modified_result() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(304, headers={"ETag": '"v2"'}, request=request)
    )
    async with httpx.AsyncClient(transport=transport) as client:
        result = await HttpContentFetcher(
            client,
            IngestionConfig(),
            url_guard=MockURLGuard(),
        ).fetch(FetchRequest("https://example.com/feed", "source"))
    assert result.not_modified is True
    assert result.etag == '"v2"'
    assert result.body == b""
