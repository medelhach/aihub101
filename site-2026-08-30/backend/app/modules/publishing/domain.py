from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class StorySection:
    heading: str
    body: str


@dataclass(frozen=True, slots=True)
class ComposedStory:
    headline: str
    dek: str
    dateline: str
    lead: str
    sections: tuple[StorySection, ...]
    key_facts: tuple[str, ...]
    entities: tuple[str, ...]
    body_markdown: str
    word_count: int
    generation_method: str
    tags: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PublishedStory:
    id: UUID
    slug: str
    section: str
    headline: str
    dek: str
    dateline: str
    lead: str
    sections: tuple[dict[str, str], ...]
    key_facts: tuple[str, ...]
    entities: tuple[str, ...]
    body_markdown: str
    tags: tuple[str, ...]
    source_name: str
    source_url: str
    canonical_url: str
    author: str | None
    published_at: datetime | None
    word_count: int
    language: str
    hero_image_url: str | None
    generation_method: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class PendingCandidate:
    id: UUID
    source_id: UUID
    source_key: str
    source_name: str
    section: str
    title: str
    summary: str | None
    published_at: datetime | None
    author: str | None
    url: str
    canonical_url: str | None
    tags: tuple[str, ...]
    images: tuple[str, ...]
    language: str
    allowed_domains: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CycleResult:
    sources_processed: int
    candidates_created: int
    stories_published: int
    stories_skipped: int
    models_seeded: int
    details: dict[str, Any]
