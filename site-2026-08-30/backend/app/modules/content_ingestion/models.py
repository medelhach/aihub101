from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, HttpUrl


@dataclass(frozen=True, slots=True)
class SourceDescriptor:
    id: str
    name: str
    content_type: str
    language: str = "en"


@dataclass(frozen=True, slots=True)
class FetchRequest:
    url: str
    source_id: str
    headers: dict[str, str] = field(default_factory=dict)
    allowed_domains: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FetchedContent:
    request: FetchRequest
    body: bytes
    content_type: str | None
    encoding: str
    status_code: int
    fetched_at: datetime
    final_url: str
    etag: str | None = None
    last_modified: str | None = None
    not_modified: bool = False


@dataclass(frozen=True, slots=True)
class ParsedContent:
    title: str | None
    summary: str | None
    published_at: datetime | str | None
    author: str | None
    url: str | None
    canonical_url: str | None = None
    language: str | None = None
    tags: tuple[str, ...] = ()
    images: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class NormalizedContent(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str
    summary: str | None = None
    published_at: datetime | None = None
    author: str | None = None
    url: HttpUrl
    canonical_url: HttpUrl | None = None
    source: SourceDescriptor
    language: str
    content_type: str
    tags: tuple[str, ...] = ()
    images: tuple[HttpUrl, ...] = ()
    content_hash: str


@dataclass(frozen=True, slots=True)
class DuplicateAssessment:
    is_duplicate: bool
    matched_id: str | None = None
    confidence: float | None = None
    strategy: str | None = None
