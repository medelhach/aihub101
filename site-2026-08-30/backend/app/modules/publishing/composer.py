from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from urllib.parse import urlsplit

from app.modules.publishing.domain import ComposedStory, StorySection
from app.modules.publishing.extraction import normalize_whitespace, strip_html

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_PROPER_NOUN = re.compile(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){0,3})\b")
_STOP_ENTITIES = {
    "The",
    "A",
    "An",
    "This",
    "That",
    "In",
    "On",
    "According",
    "However",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
}


def _sentences(text: str) -> list[str]:
    cleaned = normalize_whitespace(strip_html(text))
    parts = [part.strip() for part in _SENTENCE_SPLIT.split(cleaned) if len(part.strip()) > 40]
    return parts


def _score_sentences(sentences: list[str]) -> list[str]:
    words: Counter[str] = Counter()
    for sentence in sentences:
        for word in re.findall(r"[A-Za-z]{4,}", sentence.casefold()):
            words[word] += 1
    ranked = sorted(
        sentences,
        key=lambda sentence: sum(
            words[word] for word in re.findall(r"[A-Za-z]{4,}", sentence.casefold())
        ),
        reverse=True,
    )
    ordered: list[str] = []
    seen: set[str] = set()
    for sentence in ranked:
        key = sentence.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(sentence)
    return ordered


def _entities(text: str) -> tuple[str, ...]:
    found: list[str] = []
    seen: set[str] = set()
    for match in _PROPER_NOUN.findall(text):
        if match in _STOP_ENTITIES or match.casefold() in seen:
            continue
        seen.add(match.casefold())
        found.append(match)
        if len(found) >= 12:
            break
    return tuple(found)


def _why_it_matters(title: str, tags: tuple[str, ...], entities: tuple[str, ...]) -> str:
    haystack = f"{title} {' '.join(tags)}".casefold()
    if any(token in haystack for token in ("regulat", "policy", "law", "eu ai", "copyright")):
        theme = (
            "The development sits at the intersection of AI capability and public rules, "
            "which can change how products are shipped, audited, or restricted."
        )
    elif any(token in haystack for token in ("fund", "invest", "acquisition", "ipo", "valuat")):
        theme = (
            "Capital allocation is a leading indicator of where the industry will place "
            "compute, talent, and product bets over the next product cycle."
        )
    elif any(
        token in haystack for token in ("model", "llm", "gpt", "claude", "gemini", "open source")
    ):
        theme = (
            "Model releases reshape the practical trade-offs teams make on quality, cost, "
            "latency, licensing, and deployment control."
        )
    elif any(token in haystack for token in ("research", "paper", "arxiv", "benchmark")):
        theme = (
            "Research results often precede product capability by months. Tracking the "
            "method, data, and limitations matters more than the headline score."
        )
    elif any(token in haystack for token in ("safety", "security", "jailbreak", "misuse")):
        theme = (
            "Safety and security findings affect enterprise adoption, evaluation checklists, "
            "and whether a system can be used in high-stakes workflows."
        )
    else:
        theme = (
            "The story is relevant because it changes what practitioners, operators, or "
            "policymakers can assume about the current AI landscape."
        )
    involved = ", ".join(entities[:4]) if entities else "the organizations named in the source"
    return (
        f"{theme} Parties to watch include {involved}. Readers should treat vendor claims as "
        "claims until they are corroborated by documentation, independent evaluation, or "
        "multiple primary sources."
    )


def _background(section: str, source_name: str) -> str:
    if section == "articles":
        return (
            f"This briefing is based on material published by {source_name}. It is written as "
            "an explainer-style article for practitioners: what was introduced, how it works at "
            "a high level, what evidence is offered, and which caveats remain. It is not a "
            "substitute for the original paper, documentation, or blog post."
        )
    return (
        f"{source_name} is one of the outlets the Hub monitors for consequential AI coverage. "
        "The Hub does not republish the original article in full. This brief reconstructs the "
        "newsworthy facts, attributes them to the publisher, and adds independent context so "
        "readers can decide whether to open the source."
    )


def _next_steps(section: str) -> str:
    if section == "articles":
        return (
            "Readers evaluating the work should inspect the primary artifact next: the paper, "
            "model card, repository, or product documentation. Check whether benchmarks are "
            "comparable, whether data and evaluation are documented, and whether the claimed "
            "gains hold outside the author's test suite."
        )
    return (
        "The practical next step is to verify the claim against a primary source—an official "
        "announcement, filing, paper, or product page—and then watch for follow-on reporting "
        "that adds independent measurement, pricing, or safety detail."
    )


def compose_story(
    *,
    title: str,
    summary: str | None,
    source_name: str,
    source_url: str,
    published_at: datetime | None,
    author: str | None,
    paragraphs: tuple[str, ...],
    tags: tuple[str, ...],
    section: str,
    generation_method: str = "editorial_composer",
) -> ComposedStory:
    host = urlsplit(source_url).hostname or source_name
    date_label = published_at.strftime("%B %d, %Y") if published_at else "Undated"
    dateline = f"{source_name.upper()} — {date_label}"
    combined = " ".join((summary or "", *paragraphs))
    sentences = _sentences(combined) or _sentences(title + ". " + (summary or title))
    ranked = _score_sentences(sentences)
    lead_source = sentences[0] if sentences else title
    dek = (summary and normalize_whitespace(strip_html(summary))[:280]) or (
        ranked[0][:240] if ranked else title
    )
    if len(dek) < 80:
        dek = (
            f"{title}. Reporting from {source_name} describes a development that belongs on "
            "the AI industry brief because it affects products, research, or policy."
        )
    lead = (
        f"{lead_source} The report was published by {source_name}"
        f"{f' and credited to {author}' if author else ''} on {date_label}. "
        f"The original account is available at {host}."
    )
    entities = _entities(f"{title} {combined}")
    what_happened = " ".join(sentences[:6]) or f"{source_name} reported: {title}."
    if len(what_happened.split()) < 80:
        extra = " ".join(paragraphs[:4])
        what_happened = normalize_whitespace(f"{what_happened} {extra}")
    supporting = " ".join(ranked[1:8])
    if len(supporting.split()) < 60:
        supporting = " ".join(paragraphs[1:8]) or supporting
    key_facts = []
    if published_at:
        key_facts.append(f"Publication date: {date_label}.")
    key_facts.append(f"Primary publisher: {source_name}.")
    if author:
        key_facts.append(f"Bylined or attributed to: {author}.")
    key_facts.append(f"Original URL: {source_url}.")
    for sentence in ranked[:8]:
        if re.search(r"\d", sentence) or any(
            token in sentence.casefold()
            for token in ("announc", "launch", "releas", "model", "billion", "million", "partner")
        ):
            fact = sentence if sentence.endswith((".", "!", "?")) else f"{sentence}."
            if fact not in key_facts:
                key_facts.append(fact)
        if len(key_facts) >= 8:
            break
    while len(key_facts) < 5:
        key_facts.append(
            "Independent confirmation should be sought before treating vendor or single-outlet "
            "claims as settled fact."
        )
        break
    why = _why_it_matters(title, tags, entities)
    background = _background(section, source_name)
    involved = (
        f"Named organizations and concepts in the source material include "
        f"{', '.join(entities[:8])}."
        if entities
        else f"{source_name} is the accountable publisher for the underlying report."
    )
    if author:
        involved += f" The piece is attributed to {author}."
    next_steps = _next_steps(section)
    context = (
        f"AI coverage moves quickly and often repeats the same announcement across many outlets. "
        f"This Hub brief groups the essential facts from {source_name} and keeps the original "
        "link attached so readers can inspect wording, methodology, and updates. Nothing here "
        "is investment, legal, or safety advice."
    )
    if supporting:
        context = f"{context} Additional detail reported in the source includes: {supporting}"

    sections = (
        StorySection("What happened", what_happened),
        StorySection("Why it matters", why),
        StorySection("Key facts", "\n".join(f"- {fact}" for fact in key_facts)),
        StorySection("Who is involved", involved),
        StorySection("Background", background),
        StorySection("Context and reporting notes", context),
        StorySection("What to watch next", next_steps),
        StorySection(
            "Primary source",
            f"Read the original {source_name} item: {source_url}. The Hub summary is original "
            "editorial structuring of attributed facts, not a reprint of the publisher's article.",
        ),
    )
    body_parts = [
        f"# {title}",
        f"*{dek}*",
        f"**{dateline}**",
        lead,
    ]
    for section_block in sections:
        body_parts.append(f"## {section_block.heading}")
        body_parts.append(section_block.body)
    body_markdown = "\n\n".join(body_parts)
    word_count = len(re.findall(r"\b[\w'-]+\b", body_markdown))
    headline = title.strip()
    story_tags = tuple(dict.fromkeys((*tags, section, "artificial-intelligence")))
    return ComposedStory(
        headline=headline,
        dek=dek,
        dateline=dateline,
        lead=lead,
        sections=sections,
        key_facts=tuple(key_facts),
        entities=entities,
        body_markdown=body_markdown,
        word_count=word_count,
        generation_method=generation_method,
        tags=story_tags,
    )
