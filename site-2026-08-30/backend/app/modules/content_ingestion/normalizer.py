from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from hashlib import sha256

from pydantic import ValidationError as PydanticValidationError

from app.modules.content_ingestion.exceptions import ContentValidationError
from app.modules.content_ingestion.models import (
    NormalizedContent,
    ParsedContent,
    SourceDescriptor,
)


class DefaultContentNormalizer:
    def normalize(self, content: ParsedContent, source: SourceDescriptor) -> NormalizedContent:
        title = _required(content.title, "title")
        url = _required(content.url, "url")
        published_at = _parse_date(content.published_at)
        language = (content.language or source.language).strip().lower()
        summary = _optional(content.summary)
        canonical_url = _optional(content.canonical_url)
        digest_source = "\n".join(
            (title.casefold(), canonical_url or url, summary or "", str(published_at or ""))
        )
        try:
            return NormalizedContent(
                title=title,
                summary=summary,
                published_at=published_at,
                author=_optional(content.author),
                url=url,
                canonical_url=canonical_url,
                source=source,
                language=language,
                content_type=source.content_type,
                tags=tuple(
                    dict.fromkeys(tag.strip().casefold() for tag in content.tags if tag.strip())
                ),
                images=content.images,
                content_hash=sha256(digest_source.encode("utf-8")).hexdigest(),
            )
        except PydanticValidationError as exc:
            raise ContentValidationError(
                "Normalized content is invalid.",
                details={"errors": exc.errors(include_context=False)},
            ) from exc


def _parse_date(value: datetime | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        normalized = value.strip()
        if not normalized:
            return None
        try:
            parsed = parsedate_to_datetime(normalized)
        except (TypeError, ValueError):
            try:
                parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ContentValidationError(
                    "published_at contains an invalid date.",
                    details={"field": "published_at"},
                ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _required(value: str | None, field: str) -> str:
    normalized = _optional(value)
    if normalized is None:
        raise ContentValidationError(
            f"{field} is required.",
            details={"field": field},
        )
    return normalized


def _optional(value: str | None) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None
