from collections.abc import Sequence
from xml.etree.ElementTree import Element

from defusedxml import ElementTree

from app.modules.content_ingestion.exceptions import ParseError
from app.modules.content_ingestion.models import FetchedContent, ParsedContent
from app.modules.content_ingestion.parsers.common import collect_item_images, decode_body


class AtomParser:
    name = "atom"

    def parse(self, content: FetchedContent) -> Sequence[ParsedContent]:
        try:
            root = ElementTree.fromstring(decode_body(content))
        except ElementTree.ParseError as exc:
            raise ParseError("Atom XML is invalid.") from exc

        items: list[ParsedContent] = []
        for entry in root.findall("{*}entry"):
            alternate = next(
                (
                    link.attrib.get("href")
                    for link in entry.findall("{*}link")
                    if link.attrib.get("rel", "alternate") == "alternate"
                ),
                None,
            )
            author = entry.find("{*}author")
            items.append(
                ParsedContent(
                    title=_text(entry, "{*}title"),
                    summary=_text(entry, "{*}summary") or _text(entry, "{*}content"),
                    published_at=_text(entry, "{*}published") or _text(entry, "{*}updated"),
                    author=_text(author, "{*}name") if author is not None else None,
                    url=alternate or _text(entry, "{*}id"),
                    tags=tuple(
                        term
                        for category in entry.findall("{*}category")
                        if (term := category.attrib.get("term"))
                    ),
                    images=collect_item_images(entry),
                )
            )
        return items


def _text(element: Element, path: str) -> str | None:
    child = element.find(path)
    value = child.text.strip() if child is not None and child.text else ""
    return value or None
