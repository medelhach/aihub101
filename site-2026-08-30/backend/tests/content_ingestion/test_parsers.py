from app.modules.content_ingestion.parsers.atom import AtomParser
from app.modules.content_ingestion.parsers.html import HTMLMetadataParser
from app.modules.content_ingestion.parsers.json import JSONContentParser
from app.modules.content_ingestion.parsers.rss import RSSParser
from tests.content_ingestion.helpers import fetched


def test_rss_parser() -> None:
    content = fetched(
        """<rss><channel><item><title>Release</title>
        <link>https://example.com/release</link><description>Summary</description>
        <pubDate>Wed, 19 Aug 2026 12:00:00 GMT</pubDate>
        <category>Models</category></item></channel></rss>"""
    )
    item = RSSParser().parse(content)[0]
    assert item.title == "Release"
    assert item.url == "https://example.com/release"
    assert item.tags == ("Models",)


def test_atom_parser() -> None:
    content = fetched(
        """<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Update</title>
        <link href="https://example.com/update"/><updated>2026-08-19T12:00:00Z</updated>
        <author><name>Ada</name></author></entry></feed>"""
    )
    item = AtomParser().parse(content)[0]
    assert item.title == "Update"
    assert item.author == "Ada"


def test_json_parser() -> None:
    item = JSONContentParser().parse(
        fetched('{"items":[{"title":"JSON item","url":"https://example.com/json","tags":["AI"]}]}')
    )[0]
    assert item.title == "JSON item"
    assert item.tags == ("AI",)


def test_html_metadata_parser() -> None:
    item = HTMLMetadataParser().parse(
        fetched(
            """<html lang="en"><head><title>Fallback</title>
            <meta property="og:title" content="Canonical title">
            <meta name="description" content="Description">
            <link rel="canonical" href="https://example.com/page"></head></html>""",
            content_type="text/html",
        )
    )[0]
    assert item.title == "Canonical title"
    assert item.canonical_url == "https://example.com/page"
    assert item.language == "en"
