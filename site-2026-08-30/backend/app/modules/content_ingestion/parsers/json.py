import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from app.modules.content_ingestion.exceptions import ParseError
from app.modules.content_ingestion.models import FetchedContent, ParsedContent
from app.modules.content_ingestion.parsers.common import decode_body


@dataclass(frozen=True, slots=True)
class JSONFieldMap:
    title: str = "title"
    summary: str = "summary"
    published_at: str = "published_at"
    author: str = "author"
    url: str = "url"
    canonical_url: str = "canonical_url"
    language: str = "language"
    tags: str = "tags"
    images: str = "images"
    collection: str = "items"


class JSONContentParser:
    name = "json"

    def __init__(self, fields: JSONFieldMap | None = None) -> None:
        self._fields = fields or JSONFieldMap()

    def parse(self, content: FetchedContent) -> Sequence[ParsedContent]:
        try:
            payload = json.loads(decode_body(content))
        except json.JSONDecodeError as exc:
            raise ParseError("JSON content is invalid.") from exc

        records = payload.get(self._fields.collection, []) if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            raise ParseError("JSON collection must be a list.")
        return [self._parse_record(record) for record in records]

    def _parse_record(self, record: Any) -> ParsedContent:
        if not isinstance(record, Mapping):
            raise ParseError("Each JSON content item must be an object.")
        return ParsedContent(
            title=_optional_string(record.get(self._fields.title)),
            summary=_optional_string(record.get(self._fields.summary)),
            published_at=_optional_string(record.get(self._fields.published_at)),
            author=_optional_string(record.get(self._fields.author)),
            url=_optional_string(record.get(self._fields.url)),
            canonical_url=_optional_string(record.get(self._fields.canonical_url)),
            language=_optional_string(record.get(self._fields.language)),
            tags=_string_tuple(record.get(self._fields.tags)),
            images=_string_tuple(record.get(self._fields.images)),
            metadata={str(key): value for key, value in record.items()},
        )


def _optional_string(value: Any) -> str | None:
    return str(value).strip() if value is not None and str(value).strip() else None


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    values = value if isinstance(value, list) else [value]
    return tuple(str(item).strip() for item in values if str(item).strip())
