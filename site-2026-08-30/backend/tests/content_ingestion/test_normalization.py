from dataclasses import replace

import pytest

from app.modules.content_ingestion.exceptions import ContentValidationError, ParseError
from app.modules.content_ingestion.models import ParsedContent, SourceDescriptor
from app.modules.content_ingestion.normalizer import DefaultContentNormalizer
from app.modules.content_ingestion.parsers.common import decode_body
from app.modules.content_ingestion.validation import DefaultContentValidator
from tests.content_ingestion.helpers import fetched

SOURCE = SourceDescriptor(
    id="company-blog",
    name="Company Blog",
    content_type="release",
    language="en",
)


def test_normalizer_produces_stable_unified_content() -> None:
    parsed = ParsedContent(
        title="  A release  ",
        summary=" Summary ",
        published_at="2026-08-19T12:00:00Z",
        author="Ada",
        url="https://example.com/release",
        tags=("AI", "ai"),
    )
    normalized = DefaultContentNormalizer().normalize(parsed, SOURCE)
    assert normalized.title == "A release"
    assert normalized.language == "en"
    assert normalized.tags == ("ai",)
    assert len(normalized.content_hash) == 64
    DefaultContentValidator().validate(normalized)


@pytest.mark.parametrize(
    ("field", "value"),
    [("title", None), ("url", None), ("published_at", "not-a-date")],
)
def test_normalizer_rejects_required_and_invalid_values(field: str, value: str | None) -> None:
    values: dict[str, str | None] = {
        "title": "Title",
        "url": "https://example.com/item",
        "published_at": "2026-08-19T12:00:00Z",
    }
    values[field] = value
    with pytest.raises(ContentValidationError):
        DefaultContentNormalizer().normalize(
            ParsedContent(
                title=values["title"],
                url=values["url"],
                published_at=values["published_at"],
                summary=None,
                author=None,
            ),
            SOURCE,
        )


def test_validator_rejects_invalid_language() -> None:
    normalized = DefaultContentNormalizer().normalize(
        ParsedContent(
            title="Title",
            summary=None,
            published_at=None,
            author=None,
            url="https://example.com/item",
        ),
        SourceDescriptor("source", "Source", "generic", "invalid_language"),
    )
    with pytest.raises(ContentValidationError):
        DefaultContentValidator().validate(normalized)


def test_decode_rejects_unknown_encoding() -> None:
    with pytest.raises(ParseError):
        decode_body(replace(fetched("content"), encoding="unknown-encoding"))
