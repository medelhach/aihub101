from html.parser import HTMLParser
from re import sub


class _ParagraphCollector(HTMLParser):
    _SKIP = {"script", "style", "noscript", "nav", "footer", "header", "aside", "form"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._buffer: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._SKIP:
            self._skip_depth += 1
        if tag in {"p", "br", "li", "h1", "h2", "h3"} and self._skip_depth == 0:
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "li", "h1", "h2", "h3", "div", "article", "section"}:
            self._flush()
        if tag in self._SKIP and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._buffer.append(data)

    def _flush(self) -> None:
        text = sub(r"\s+", " ", "".join(self._buffer)).strip()
        self._buffer.clear()
        if len(text) >= 40:
            self.paragraphs.append(text)


def extract_paragraphs(html: str) -> tuple[str, ...]:
    parser = _ParagraphCollector()
    parser.feed(html)
    parser.close()
    seen: set[str] = set()
    unique: list[str] = []
    for paragraph in parser.paragraphs:
        key = paragraph.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(paragraph)
    return tuple(unique[:40])


def strip_html(value: str) -> str:
    return sub(r"<[^>]+>", " ", value)


def normalize_whitespace(value: str) -> str:
    return sub(r"\s+", " ", value).strip()
