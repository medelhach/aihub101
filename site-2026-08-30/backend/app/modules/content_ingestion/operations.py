from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.modules.content_ingestion.models import NormalizedContent


class RunStatus(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    DEAD_LETTERED = "dead_lettered"


@dataclass(frozen=True, slots=True)
class RegisteredSource:
    id: UUID
    key: str
    name: str
    source_type: str
    endpoint_url: str
    parser_name: str
    content_type: str
    language: str
    enabled: bool
    allowed_domains: tuple[str, ...]
    poll_interval_seconds: int


@dataclass(frozen=True, slots=True)
class SourceCheckpoint:
    source_id: UUID
    etag: str | None = None
    last_modified: str | None = None
    last_successful_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class FetchProvenance:
    final_url: str
    fetched_at: datetime
    status_code: int
    etag: str | None = None
    last_modified: str | None = None


@dataclass(frozen=True, slots=True)
class RunRecord:
    id: UUID
    source_id: UUID
    idempotency_key: str
    status: RunStatus
    attempt_count: int = 1
    acquired: bool = False


@dataclass(frozen=True, slots=True)
class CandidateRecord:
    id: UUID
    source_id: UUID
    run_id: UUID
    content: NormalizedContent


@dataclass(frozen=True, slots=True)
class DeadLetter:
    source_id: UUID
    run_id: UUID | None
    error_code: str
    message: str
    failed_at: datetime
    attempts: int
