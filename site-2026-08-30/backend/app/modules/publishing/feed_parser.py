from collections.abc import Sequence

from app.modules.content_ingestion.exceptions import ParseError
from app.modules.content_ingestion.models import FetchedContent, ParsedContent
from app.modules.content_ingestion.parsers.atom import AtomParser
from app.modules.content_ingestion.parsers.rss import RSSParser


class TolerantFeedParser:
    """Accept RSS or Atom regardless of how the source was registered."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._rss = RSSParser()
        self._atom = AtomParser()

    def parse(self, content: FetchedContent) -> Sequence[ParsedContent]:
        try:
            items = self._rss.parse(content)
            if items:
                return items
        except ParseError:
            items = ()
        return self._atom.parse(content)
