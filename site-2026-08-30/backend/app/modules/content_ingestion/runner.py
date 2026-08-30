from collections.abc import Callable
from dataclasses import dataclass
from logging import Logger, LoggerAdapter
from typing import Protocol

from app.core.exceptions import AppError
from app.modules.content_ingestion.interfaces import (
    ContentSource,
    DeadLetterSink,
    IngestionMetrics,
    IngestionOperationsRepository,
    SourceRegistryRepository,
)
from app.modules.content_ingestion.operations import (
    DeadLetter,
    RegisteredSource,
    RunStatus,
    SourceCheckpoint,
)
from app.modules.content_ingestion.service import IngestionRun
from app.utils.datetime import utc_now

SourceAdapterFactory = Callable[
    [RegisteredSource, SourceCheckpoint | None],
    ContentSource,
]


class IngestionEngine(Protocol):
    async def ingest(self, source: ContentSource) -> IngestionRun: ...


class SourceAdapterRegistry:
    def __init__(self, factories: dict[str, SourceAdapterFactory]) -> None:
        self._factories = dict(factories)

    def build(
        self,
        source: RegisteredSource,
        checkpoint: SourceCheckpoint | None,
    ) -> ContentSource:
        try:
            factory = self._factories[source.source_type]
        except KeyError as error:
            raise ValueError(
                f"No adapter is registered for source type '{source.source_type}'."
            ) from error
        return factory(source, checkpoint)


@dataclass(frozen=True, slots=True)
class RunExecution:
    status: RunStatus
    run_id: str
    item_count: int
    attempt_count: int


class IngestionRunner:
    def __init__(
        self,
        *,
        sources: SourceRegistryRepository,
        operations: IngestionOperationsRepository,
        adapters: SourceAdapterRegistry,
        engine: IngestionEngine,
        metrics: IngestionMetrics,
        dead_letters: DeadLetterSink,
        logger: LoggerAdapter[Logger],
        max_attempts: int = 3,
    ) -> None:
        self._sources = sources
        self._operations = operations
        self._adapters = adapters
        self._engine = engine
        self._metrics = metrics
        self._dead_letters = dead_letters
        self._logger = logger
        self._max_attempts = max_attempts

    async def run(self, source_key: str, idempotency_key: str) -> RunExecution:
        source = await self._sources.get_by_key(source_key)
        if source is None:
            raise ValueError(f"Unknown ingestion source '{source_key}'.")

        run = await self._operations.start_run(source.id, idempotency_key)
        if not run.acquired:
            return RunExecution(
                status=run.status,
                run_id=str(run.id),
                item_count=0,
                attempt_count=run.attempt_count,
            )

        self._metrics.run_started(source.key)
        if not source.enabled:
            await self._operations.complete_run(run.id, RunStatus.SKIPPED, item_count=0)
            self._metrics.run_completed(source.key, RunStatus.SKIPPED, 0)
            return RunExecution(RunStatus.SKIPPED, str(run.id), 0, run.attempt_count)

        try:
            checkpoint = await self._operations.get_checkpoint(source.id)
            adapter = self._adapters.build(source, checkpoint)
            ingestion = await self._engine.ingest(adapter)
            contents = tuple(item.content for item in ingestion.items)
            item_count = await self._operations.save_candidates(
                source.id,
                run.id,
                contents,
                ingestion.provenance,
            )
            await self._operations.update_checkpoint(
                SourceCheckpoint(
                    source_id=source.id,
                    etag=ingestion.response_etag or (checkpoint.etag if checkpoint else None),
                    last_modified=ingestion.response_last_modified
                    or (checkpoint.last_modified if checkpoint else None),
                    last_successful_at=utc_now(),
                )
            )
            status = RunStatus.SKIPPED if ingestion.not_modified else RunStatus.SUCCEEDED
            await self._operations.complete_run(run.id, status, item_count=item_count)
            self._metrics.run_completed(source.key, status, item_count)
            self._logger.info(
                "ingestion_run_completed",
                extra={
                    "source_key": source.key,
                    "run_id": str(run.id),
                    "status": status,
                    "item_count": item_count,
                },
            )
            return RunExecution(status, str(run.id), item_count, run.attempt_count)
        except Exception as error:
            code, message = self._safe_error(error)
            terminal = run.attempt_count >= self._max_attempts
            status = RunStatus.DEAD_LETTERED if terminal else RunStatus.FAILED
            if terminal:
                await self._dead_letters.publish(
                    DeadLetter(
                        source_id=source.id,
                        run_id=run.id,
                        error_code=code,
                        message=message,
                        failed_at=utc_now(),
                        attempts=run.attempt_count,
                    )
                )
            await self._operations.complete_run(
                run.id,
                status,
                item_count=0,
                error_code=code,
                error_message=message,
            )
            self._metrics.run_failed(source.key, code)
            self._logger.error(
                "ingestion_run_failed",
                extra={
                    "source_key": source.key,
                    "run_id": str(run.id),
                    "error_code": code,
                    "attempt_count": run.attempt_count,
                    "status": status,
                },
                exc_info=True,
            )
            return RunExecution(status, str(run.id), 0, run.attempt_count)

    @staticmethod
    def _safe_error(error: Exception) -> tuple[str, str]:
        if isinstance(error, AppError):
            return error.code, error.message[:2000]
        return "unexpected_ingestion_error", "The ingestion run failed unexpectedly."
