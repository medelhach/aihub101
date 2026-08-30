from collections.abc import Sequence
from html.parser import HTMLParser

from app.modules.content_ingestion.models import FetchedContent, ParsedContent
from app.modules.content_ingestion.parsers.common import decode_body


class HTMLMetadataParser:
    name = "html"

    def parse(self, content: FetchedContent) -> Sequence[ParsedContent]:
        collector = _MetadataCollector()
        collector.feed(decode_body(content))
        metadata = collector.metadata
        keywords = metadata.get("keywords", "")
        image = metadata.get("og:image") or metadata.get("twitter:image")
        return [
            ParsedContent(
                title=metadata.get("og:title") or collector.title,
                summary=metadata.get("description") or metadata.get("og:description"),
                published_at=metadata.get("article:published_time"),
                author=metadata.get("author") or metadata.get("article:author"),
                url=metadata.get("og:url") or content.final_url,
                canonical_url=collector.canonical_url,
                language=collector.language,
                tags=tuple(tag.strip() for tag in keywords.split(",") if tag.strip()),
                images=(image,) if image else (),
                metadata=metadata,
            )
        ]


class _MetadataCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.metadata: dict[str, str] = {}
        self.title: str | None = None
        self.canonical_url: str | None = None
        self.language: str | None = None
        self._in_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value for key, value in attrs if value is not None}
        if tag == "html":
            self.language = attributes.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = attributes.get("property") or attributes.get("name")
            value = attributes.get("content")
            if key and value:
                self.metadata[key.lower()] = value.strip()
        elif (
            tag == "link"
            and attributes.get("rel", "").lower() == "canonical"
            and attributes.get("href")
        ):
            self.canonical_url = attributes["href"]

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
            value = "".join(self._title_parts).strip()
            self.title = value or None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
