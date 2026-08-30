from datetime import UTC, datetime

from app.modules.content_ingestion.models import FetchedContent, FetchRequest


def fetched(
    body: str,
    *,
    content_type: str = "text/plain",
    encoding: str = "utf-8",
    url: str = "https://example.com/feed",
) -> FetchedContent:
    request = FetchRequest(url=url, source_id="test-source")
    return FetchedContent(
        request=request,
        body=body.encode(encoding),
        content_type=content_type,
        encoding=encoding,
        status_code=200,
        fetched_at=datetime.now(UTC),
        final_url=url,
    )
