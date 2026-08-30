from collections.abc import Sequence

from app.modules.content_ingestion.models import FetchRequest, SourceDescriptor
from app.modules.content_ingestion.operations import RegisteredSource, SourceCheckpoint


class RSSSource:
    parser_name = "rss"

    def __init__(
        self,
        source: RegisteredSource,
        checkpoint: SourceCheckpoint | None = None,
    ) -> None:
        if source.source_type != "rss" or source.parser_name != "rss":
            raise ValueError("RSSSource requires an RSS source registration.")
        self._source = source
        self._checkpoint = checkpoint
        self.descriptor = SourceDescriptor(
            id=source.key,
            name=source.name,
            content_type=source.content_type,
            language=source.language,
        )

    async def build_requests(self) -> Sequence[FetchRequest]:
        headers: dict[str, str] = {}
        if self._checkpoint and self._checkpoint.etag:
            headers["If-None-Match"] = self._checkpoint.etag
        if self._checkpoint and self._checkpoint.last_modified:
            headers["If-Modified-Since"] = self._checkpoint.last_modified
        return [
            FetchRequest(
                url=self._source.endpoint_url,
                source_id=self._source.key,
                headers=headers,
                allowed_domains=self._source.allowed_domains,
            )
        ]
