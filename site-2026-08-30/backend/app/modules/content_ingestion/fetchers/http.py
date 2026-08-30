import asyncio
from collections.abc import Awaitable, Callable
from urllib.parse import urljoin, urlsplit

import httpx

from app.modules.content_ingestion.config import IngestionConfig
from app.modules.content_ingestion.exceptions import ContentTooLargeError, FetchError
from app.modules.content_ingestion.interfaces import RateLimiter, URLGuard
from app.modules.content_ingestion.models import FetchedContent, FetchRequest
from app.utils.datetime import utc_now

_REDIRECT_STATUS = {301, 302, 303, 307, 308}


class HttpContentFetcher:
    def __init__(
        self,
        client: httpx.AsyncClient,
        config: IngestionConfig,
        *,
        url_guard: URLGuard,
        rate_limiter: RateLimiter | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        max_redirects: int = 0,
    ) -> None:
        if client.follow_redirects:
            raise ValueError("The ingestion HTTP client must not follow redirects automatically.")
        self._client = client
        self._config = config
        self._url_guard = url_guard
        self._rate_limiter = rate_limiter
        self._sleep = sleep
        self._max_redirects = max_redirects

    async def fetch(self, request: FetchRequest) -> FetchedContent:
        if self._rate_limiter is not None:
            await self._rate_limiter.acquire(request.source_id)

        current = request
        headers = {"User-Agent": self._config.user_agent, **request.headers}
        for hop in range(self._max_redirects + 1):
            await self._url_guard.validate(current.url, current.allowed_domains)
            fetched, location = await self._download(current, headers)
            if location is None:
                return fetched
            if hop >= self._max_redirects:
                break
            current = self._redirected_request(current, location)
        raise FetchError(
            "Unable to fetch content.",
            details={"source_id": request.source_id, "url": request.url},
        )

    async def _download(
        self, request: FetchRequest, headers: dict[str, str]
    ) -> tuple[FetchedContent, str | None]:
        attempts = self._config.retries + 1
        for attempt in range(attempts):
            try:
                async with self._client.stream(
                    "GET",
                    request.url,
                    headers=headers,
                    timeout=self._config.timeout_seconds,
                ) as response:
                    if response.status_code in _REDIRECT_STATUS:
                        return (
                            FetchedContent(
                                request=request,
                                body=b"",
                                content_type=response.headers.get("content-type"),
                                encoding=response.encoding or "utf-8",
                                status_code=response.status_code,
                                fetched_at=utc_now(),
                                final_url=str(response.url),
                            ),
                            response.headers.get("location"),
                        )
                    if response.status_code == 304:
                        return (
                            FetchedContent(
                                request=request,
                                body=b"",
                                content_type=response.headers.get("content-type"),
                                encoding=response.encoding or "utf-8",
                                status_code=304,
                                fetched_at=utc_now(),
                                final_url=str(response.url),
                                etag=response.headers.get("etag"),
                                last_modified=response.headers.get("last-modified"),
                                not_modified=True,
                            ),
                            None,
                        )
                    if response.status_code == 429 or response.status_code >= 500:
                        if attempt < attempts - 1:
                            await self._sleep(self._retry_delay(attempt, response))
                            continue
                    response.raise_for_status()
                    declared_size = self._declared_size(response)
                    if declared_size > self._config.maximum_article_size_bytes:
                        raise ContentTooLargeError(
                            "Fetched content exceeds the configured size limit."
                        )
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > self._config.maximum_article_size_bytes:
                            raise ContentTooLargeError(
                                "Fetched content exceeds the configured size limit."
                            )
                    return (
                        FetchedContent(
                            request=request,
                            body=bytes(body),
                            content_type=response.headers.get("content-type"),
                            encoding=response.encoding or "utf-8",
                            status_code=response.status_code,
                            fetched_at=utc_now(),
                            final_url=str(response.url),
                            etag=response.headers.get("etag"),
                            last_modified=response.headers.get("last-modified"),
                        ),
                        None,
                    )
            except ContentTooLargeError:
                raise
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
                if attempt >= attempts - 1 or (
                    isinstance(exc, httpx.HTTPStatusError)
                    and exc.response.status_code < 500
                    and exc.response.status_code != 429
                ):
                    raise FetchError(
                        "Unable to fetch content.",
                        details={"source_id": request.source_id, "url": request.url},
                    ) from exc
                await self._sleep(2**attempt)
        raise FetchError("Unable to fetch content.")

    @staticmethod
    def _redirected_request(request: FetchRequest, location: str) -> FetchRequest:
        next_url = urljoin(request.url, location)
        hostname = (urlsplit(next_url).hostname or "").rstrip(".")
        allowed = request.allowed_domains
        if hostname and hostname.casefold() not in {item.casefold() for item in allowed}:
            allowed = (*allowed, hostname)
        return FetchRequest(
            url=next_url,
            source_id=request.source_id,
            headers=request.headers,
            allowed_domains=allowed,
        )

    @staticmethod
    def _retry_delay(attempt: int, response: httpx.Response) -> float:
        retry_after = response.headers.get("retry-after")
        if retry_after and retry_after.isdigit():
            return min(float(retry_after), 60.0)
        return float(2**attempt)

    @staticmethod
    def _declared_size(response: httpx.Response) -> int:
        value = response.headers.get("content-length")
        if value is None:
            return 0
        try:
            return max(0, int(value))
        except ValueError:
            return 0
