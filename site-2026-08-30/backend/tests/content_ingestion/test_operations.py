from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.core.logging import get_logger
from app.modules.content_ingestion.interfaces import ContentSource
from app.modules.content_ingestion.models import (
    DuplicateAssessment,
    NormalizedContent,
)
from app.modules.content_ingestion.operations import (
    DeadLetter,
    FetchProvenance,
    RegisteredSource,
    RunRecord,
    RunStatus,
    SourceCheckpoint,
)
from app.modules.content_ingestion.rss_source import RSSSource
from app.modules.content_ingestion.runner import (
    IngestionRunner,
    SourceAdapterRegistry,
)
from app.modules.content_ingestion.security import SSRFGuard
from app.modules.content_ingestion.service import IngestionItem, IngestionRun


def registered_source(*, enabled: bool = True) -> RegisteredSource:
    return RegisteredSource(
        id=uuid4(),
        key="example-rss",
        name="Example",
        source_type="rss",
        endpoint_url="https://feeds.example.com/rss",
        parser_name="rss",
        content_type="feed",
        language="en",
        enabled=enabled,
        allowed_domains=("example.com",),
        poll_interval_seconds=300,
    )


class PublicGuard(SSRFGuard):
    @staticmethod
    def _resolve(hostname: str, port: int | None) -> set[str]:
        return {"93.184.216.34"}


class PrivateGuard(SSRFGuard):
    @staticmethod
    def _resolve(hostname: str, port: int | None) -> set[str]:
        return {"127.0.0.1"}


@pytest.mark.asyncio
async def test_ssrf_guard_enforces_allowlist_and_public_resolution() -> None:
    await PublicGuard().validate("https://feeds.example.com/rss", ("example.com",))
    with pytest.raises(Exception, match="allowlisted"):
        await PublicGuard().validate("https://attacker.example/rss", ("example.com",))
    with pytest.raises(Exception, match="non-public"):
        await PrivateGuard().validate("https://example.com/rss", ("example.com",))


@pytest.mark.asyncio
async def test_rss_source_applies_conditional_headers() -> None:
    source = registered_source()
    checkpoint = SourceCheckpoint(
        source.id, etag='"v1"', last_modified="Wed, 19 Aug 2026 10:00:00 GMT"
    )
    request = (await RSSSource(source, checkpoint).build_requests())[0]
    assert request.headers == {
        "If-None-Match": '"v1"',
        "If-Modified-Since": "Wed, 19 Aug 2026 10:00:00 GMT",
    }
    assert request.allowed_domains == ("example.com",)


class FakeSources:
    def __init__(self, source: RegisteredSource) -> None:
        self.source = source

    async def get_by_key(self, key: str) -> RegisteredSource | None:
        return self.source if key == self.source.key else None

    async def get_by_id(self, source_id: UUID) -> RegisteredSource | None:
        return self.source if source_id == self.source.id else None

    async def list_enabled(self) -> Sequence[RegisteredSource]:
        return (self.source,) if self.source.enabled else ()

    async def save(self, source: RegisteredSource) -> RegisteredSource:
        self.source = source
        return source

    async def set_enabled(self, source_id: UUID, enabled: bool) -> bool:
        return source_id == self.source.id


class FakeOperations:
    def __init__(
        self,
        source_id: UUID,
        *,
        attempt_count: int = 1,
        acquired: bool = True,
    ) -> None:
        self.source_id = source_id
        self.run_id = uuid4()
        self.attempt_count = attempt_count
        self.acquired = acquired
        self.completed: tuple[RunStatus, int, str | None] | None = None
        self.checkpoint: SourceCheckpoint | None = None
        self.provenance: Sequence[FetchProvenance] = ()
        self.saved = 0

    async def start_run(self, source_id: UUID, idempotency_key: str) -> RunRecord:
        return RunRecord(
            self.run_id,
            source_id,
            idempotency_key,
            RunStatus.RUNNING,
            self.attempt_count,
            self.acquired,
        )

    async def find_run(self, idempotency_key: str) -> RunRecord | None:
        return None

    async def get_checkpoint(self, source_id: UUID) -> SourceCheckpoint | None:
        return None

    async def save_candidates(
        self,
        source_id: UUID,
        run_id: UUID,
        contents: Sequence[NormalizedContent],
        provenance: Sequence[FetchProvenance],
    ) -> int:
        self.saved = len(contents)
        self.provenance = provenance
        return self.saved

    async def update_checkpoint(self, checkpoint: SourceCheckpoint) -> None:
        self.checkpoint = checkpoint

    async def complete_run(
        self,
        run_id: UUID,
        status: RunStatus,
        *,
        item_count: int,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        self.completed = (status, item_count, error_code)


class FakeMetrics:
    def __init__(self) -> None:
        self.failed = 0

    def run_started(self, source_key: str) -> None:
        return None

    def run_completed(self, source_key: str, status: RunStatus, item_count: int) -> None:
        return None

    def run_failed(self, source_key: str, error_code: str) -> None:
        self.failed += 1


class FakeDeadLetters:
    def __init__(self) -> None:
        self.items: list[DeadLetter] = []

    async def publish(self, dead_letter: DeadLetter) -> None:
        self.items.append(dead_letter)


class SuccessfulEngine:
    async def ingest(self, source: ContentSource) -> IngestionRun:
        descriptor = source.descriptor
        content = NormalizedContent(
            title="Item",
            url="https://example.com/item",
            source=descriptor,
            language="en",
            content_type="feed",
            content_hash="a" * 64,
        )
        return IngestionRun(
            descriptor.id,
            (IngestionItem(content, DuplicateAssessment(False)),),
            response_etag='"v2"',
            provenance=(
                FetchProvenance(
                    final_url="https://feeds.example.com/rss",
                    fetched_at=datetime(2026, 8, 20, tzinfo=UTC),
                    status_code=200,
                    etag='"v2"',
                ),
            ),
        )


class FailedEngine:
    async def ingest(self, source: ContentSource) -> IngestionRun:
        raise RuntimeError("secret internal detail")


@pytest.mark.asyncio
async def test_runner_persists_candidates_and_checkpoint() -> None:
    source = registered_source()
    operations = FakeOperations(source.id)
    runner = IngestionRunner(
        sources=FakeSources(source),
        operations=operations,
        adapters=SourceAdapterRegistry({"rss": RSSSource}),
        engine=SuccessfulEngine(),
        metrics=FakeMetrics(),
        dead_letters=FakeDeadLetters(),
        logger=get_logger("test"),
    )
    result = await runner.run(source.key, "schedule:2026-08-20T15:00Z")
    assert result.status is RunStatus.SUCCEEDED
    assert operations.saved == 1
    assert operations.checkpoint is not None
    assert operations.checkpoint.etag == '"v2"'
    assert operations.provenance[0].status_code == 200


@pytest.mark.asyncio
async def test_runner_tracks_failure_and_dead_letters_terminal_attempt() -> None:
    source = registered_source()
    operations = FakeOperations(source.id, attempt_count=3)
    dead_letters = FakeDeadLetters()
    runner = IngestionRunner(
        sources=FakeSources(source),
        operations=operations,
        adapters=SourceAdapterRegistry({"rss": RSSSource}),
        engine=FailedEngine(),
        metrics=FakeMetrics(),
        dead_letters=dead_letters,
        logger=get_logger("test"),
        max_attempts=3,
    )
    result = await runner.run(source.key, "schedule:2026-08-20T15:00Z")
    assert result.status is RunStatus.DEAD_LETTERED
    assert operations.completed == (
        RunStatus.DEAD_LETTERED,
        0,
        "unexpected_ingestion_error",
    )
    assert dead_letters.items[0].message == "The ingestion run failed unexpectedly."


@pytest.mark.asyncio
async def test_runner_does_not_repeat_an_already_acquired_run() -> None:
    source = registered_source()
    operations = FakeOperations(source.id, acquired=False)
    runner = IngestionRunner(
        sources=FakeSources(source),
        operations=operations,
        adapters=SourceAdapterRegistry({"rss": RSSSource}),
        engine=FailedEngine(),
        metrics=FakeMetrics(),
        dead_letters=FakeDeadLetters(),
        logger=get_logger("test"),
    )
    result = await runner.run(source.key, "schedule:2026-08-20T15:00Z")
    assert result.status is RunStatus.RUNNING
    assert operations.completed is None
