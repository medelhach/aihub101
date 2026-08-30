from collections.abc import Sequence
from xml.etree.ElementTree import Element

from defusedxml import ElementTree

from app.modules.content_ingestion.exceptions import ParseError
from app.modules.content_ingestion.models import FetchedContent, ParsedContent
from app.modules.content_ingestion.parsers.common import decode_body


class RSSParser:
    name = "rss"

    def parse(self, content: FetchedContent) -> Sequence[ParsedContent]:
        try:
            root = ElementTree.fromstring(decode_body(content))
        except ElementTree.ParseError as exc:
            raise ParseError("RSS XML is invalid.") from exc

        items: list[ParsedContent] = []
        for item in root.findall(".//item"):
            images = tuple(
                enclosure.attrib["url"]
                for enclosure in item.findall("enclosure")
                if enclosure.attrib.get("type", "").startswith("image/")
                and "url" in enclosure.attrib
            )
            items.append(
                ParsedContent(
                    title=_text(item, "title"),
                    summary=_text(item, "description"),
                    published_at=_text(item, "pubDate"),
                    author=_text(item, "author") or _text(item, "{*}creator"),
                    url=_text(item, "link") or _text(item, "guid"),
                    tags=tuple(
                        value
                        for category in item.findall("category")
                        if (value := _clean(category.text))
                    ),
                    images=images,
                )
            )
        return items


def _text(element: Element, path: str) -> str | None:
    child = element.find(path)
    return _clean(child.text if child is not None else None)


def _clean(value: str | None) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None
