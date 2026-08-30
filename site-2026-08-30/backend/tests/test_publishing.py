from datetime import UTC, datetime

from app.modules.catalog.comparison import compare_models
from app.modules.catalog.records import model_catalog
from app.modules.publishing.composer import compose_story
from app.modules.publishing.extraction import extract_paragraphs
from app.modules.publishing.seed_stories import editorial_seed_candidates


def test_editorial_seed_covers_news_and_articles() -> None:
    seeds = editorial_seed_candidates()
    sections = {item[0].section for item in seeds}
    assert "news" in sections
    assert "articles" in sections
    assert len(seeds) >= 6


def test_catalog_has_at_least_fifty_unique_models() -> None:
    records = list(model_catalog())
    slugs = [str(record["slug"]) for record in records]
    assert len(records) >= 50
    assert len(slugs) == len(set(slugs))


def test_comparison_marks_differences() -> None:
    models = list(model_catalog())[:3]
    result = compare_models(models)
    assert result["summary"]["model_count"] == 3
    assert any(row["differs"] for row in result["rows"])
    assert result["rows"][0]["label"] == "Provider"


def test_composer_builds_a_full_news_brief() -> None:
    paragraphs = (
        "Acme Labs released a new language model with a 128,000 token context window on Tuesday.",
        "The company said the model is available through an API and as downloadable weights.",
        "Independent researchers have not yet reproduced the reported benchmark scores.",
        "Enterprises are evaluating whether the license allows commercial deployment.",
    )
    story = compose_story(
        title="Acme Labs launches a long-context language model",
        summary="Acme Labs introduced a 128k-context model with API and weight access.",
        source_name="Example Daily",
        source_url="https://news.example.com/acme-model",
        published_at=datetime(2026, 8, 30, 12, 0, tzinfo=UTC),
        author="Jane Reporter",
        paragraphs=paragraphs,
        tags=("models",),
        section="news",
    )
    assert story.word_count >= 250
    assert "What happened" in {section.heading for section in story.sections}
    assert "EXAMPLE DAILY" in story.dateline
    assert "https://news.example.com/acme-model" in story.body_markdown


def test_html_extraction_keeps_article_paragraphs() -> None:
    html = """
    <html><body>
      <nav>Skip this navigation region because it is short chrome.</nav>
      <article>
        <p>This is a substantial paragraph about an AI model release that should be extracted.</p>
        <p>A second paragraph explains pricing, context length, and the license for developers.</p>
      </article>
      <script>ignored()</script>
    </body></html>
    """
    paragraphs = extract_paragraphs(html)
    assert len(paragraphs) >= 2
    assert "pricing" in paragraphs[1]
