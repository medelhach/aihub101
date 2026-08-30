from collections.abc import Sequence
from datetime import timedelta
from typing import Protocol
from uuid import UUID

from app.modules.content_ingestion.models import (
    DuplicateAssessment,
    FetchedContent,
    FetchRequest,
    NormalizedContent,
    ParsedContent,
    SourceDescriptor,
)
from app.modules.content_ingestion.operations import (
    DeadLetter,
    FetchProvenance,
    RegisteredSource,
    RunRecord,
    RunStatus,
    SourceCheckpoint,
)


class ContentSource(Protocol):
    @property
    def descriptor(self) -> SourceDescriptor: ...

    @property
    def parser_name(self) -> str: ...

    async def build_requests(self) -> Sequence[FetchRequest]: ...


class ContentFetcher(Protocol):
    async def fetch(self, request: FetchRequest) -> FetchedContent: ...


class ContentParser(Protocol):
    @property
    def name(self) -> str: ...

    def parse(self, content: FetchedContent) -> Sequence[ParsedContent]: ...


class ContentNormalizer(Protocol):
    def normalize(self, content: ParsedContent, source: SourceDescriptor) -> NormalizedContent: ...


class ContentValidator(Protocol):
    def validate(self, content: NormalizedContent) -> None: ...


class DuplicateDetector(Protocol):
    async def assess(self, content: NormalizedContent) -> DuplicateAssessment: ...


class IngestionRepository(Protocol):
    async def save(self, contents: Sequence[NormalizedContent]) -> None: ...

    async def find_by_url(self, url: str) -> NormalizedContent | None: ...

    async def find_by_hash(self, content_hash: str) -> NormalizedContent | None: ...


class RateLimiter(Protocol):
    async def acquire(self, source_id: str) -> None: ...


class URLGuard(Protocol):
    async def validate(self, url: str, allowed_domains: tuple[str, ...]) -> None: ...


class IngestionScheduler(Protocol):
    async def register(self, source_id: str, interval: timedelta) -> None: ...

    async def unregister(self, source_id: str) -> None: ...


class SourceRegistryRepository(Protocol):
    async def get_by_id(self, source_id: UUID) -> RegisteredSource | None: ...

    async def get_by_key(self, key: str) -> RegisteredSource | None: ...

    async def list_enabled(self) -> Sequence[RegisteredSource]: ...

    async def save(self, source: RegisteredSource) -> RegisteredSource: ...

    async def set_enabled(self, source_id: UUID, enabled: bool) -> bool: ...


class IngestionOperationsRepository(Protocol):
    async def get_checkpoint(self, source_id: UUID) -> SourceCheckpoint | None: ...

    async def start_run(self, source_id: UUID, idempotency_key: str) -> RunRecord: ...

    async def find_run(self, idempotency_key: str) -> RunRecord | None: ...

    async def save_candidates(
        self,
        source_id: UUID,
        run_id: UUID,
        contents: Sequence[NormalizedContent],
        provenance: Sequence[FetchProvenance],
    ) -> int: ...

    async def complete_run(
        self,
        run_id: UUID,
        status: RunStatus,
        *,
        item_count: int,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None: ...

    async def update_checkpoint(self, checkpoint: SourceCheckpoint) -> None: ...


class DeadLetterSink(Protocol):
    async def publish(self, dead_letter: DeadLetter) -> None: ...


class IngestionMetrics(Protocol):
    def run_started(self, source_key: str) -> None: ...

    def run_completed(self, source_key: str, status: RunStatus, item_count: int) -> None: ...

    def run_failed(self, source_key: str, error_code: str) -> None: ...
