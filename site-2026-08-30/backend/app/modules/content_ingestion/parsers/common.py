from re import IGNORECASE, compile
from xml.etree.ElementTree import Element

from app.modules.content_ingestion.exceptions import ParseError
from app.modules.content_ingestion.models import FetchedContent

_IMG_SRC = compile(r'<img[^>]+src=["\']([^"\']+)["\']', IGNORECASE)
_MEDIA = "{http://search.yahoo.com/mrss/}"


def decode_body(content: FetchedContent) -> str:
    try:
        return content.body.decode(content.encoding)
    except (LookupError, UnicodeDecodeError) as exc:
        raise ParseError(
            "Content encoding is invalid.",
            details={"encoding": content.encoding},
        ) from exc


def collect_item_images(item: Element) -> tuple[str, ...]:
    found: list[str] = []
    seen: set[str] = set()

    def add(url: str | None) -> None:
        if not url:
            return
        cleaned = url.strip()
        if cleaned.startswith(("http://", "https://", "/")) and cleaned not in seen:
            seen.add(cleaned)
            found.append(cleaned)

    for enclosure in item.findall("enclosure") + item.findall("{*}enclosure"):
        mime = enclosure.attrib.get("type", "")
        url = enclosure.attrib.get("url") or enclosure.attrib.get("href")
        if mime.startswith("image/") or _looks_like_image(url):
            add(url)
    for node in item.findall(f"{_MEDIA}thumbnail") + item.findall(f"{_MEDIA}content"):
        mime = node.attrib.get("type", "")
        medium = node.attrib.get("medium", "image")
        if medium == "image" or mime.startswith("image/") or not mime:
            add(node.attrib.get("url"))
    for link in item.findall("{*}link"):
        mime = link.attrib.get("type", "")
        rel = link.attrib.get("rel", "")
        if mime.startswith("image/") or rel in {"enclosure", "preview"} and _looks_like_image(
            link.attrib.get("href")
        ):
            add(link.attrib.get("href"))
    for path in ("description", "{*}summary", "{*}content", "{*}description"):
        child = item.find(path)
        text = (child.text or "") if child is not None else ""
        for match in _IMG_SRC.findall(text):
            add(match)
    return tuple(found)


def _looks_like_image(url: str | None) -> bool:
    if not url:
        return False
    path = url.split("?", 1)[0].casefold()
    return path.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"))
