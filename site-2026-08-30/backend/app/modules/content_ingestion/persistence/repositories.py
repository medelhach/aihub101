from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content_ingestion.models import NormalizedContent
from app.modules.content_ingestion.operations import (
    FetchProvenance,
    RegisteredSource,
    RunRecord,
    RunStatus,
    SourceCheckpoint,
)
from app.modules.content_ingestion.persistence.models import (
    IngestionCandidateModel,
    IngestionCheckpointModel,
    IngestionRunModel,
    IngestionSourceModel,
)
from app.utils.datetime import utc_now


def _registered_source(model: IngestionSourceModel) -> RegisteredSource:
    return RegisteredSource(
        id=model.id,
        key=model.key,
        name=model.name,
        source_type=model.source_type,
        endpoint_url=model.endpoint_url,
        parser_name=model.parser_name,
        content_type=model.content_type,
        language=model.language,
        enabled=model.enabled,
        allowed_domains=tuple(model.allowed_domains),
        poll_interval_seconds=model.poll_interval_seconds,
    )


class PostgreSQLSourceRegistryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, source_id: UUID) -> RegisteredSource | None:
        model = await self._session.get(IngestionSourceModel, source_id)
        return _registered_source(model) if model else None

    async def get_by_key(self, key: str) -> RegisteredSource | None:
        model = await self._session.scalar(
            select(IngestionSourceModel).where(IngestionSourceModel.key == key)
        )
        return _registered_source(model) if model else None

    async def list_enabled(self) -> Sequence[RegisteredSource]:
        result = await self._session.scalars(
            select(IngestionSourceModel)
            .where(IngestionSourceModel.enabled.is_(True))
            .order_by(IngestionSourceModel.key)
        )
        return tuple(_registered_source(model) for model in result)

    async def save(self, source: RegisteredSource) -> RegisteredSource:
        statement = insert(IngestionSourceModel).values(
            id=source.id,
            key=source.key,
            name=source.name,
            source_type=source.source_type,
            endpoint_url=source.endpoint_url,
            parser_name=source.parser_name,
            content_type=source.content_type,
            language=source.language,
            enabled=source.enabled,
            allowed_domains=list(source.allowed_domains),
            poll_interval_seconds=source.poll_interval_seconds,
        )
        model = await self._session.scalar(
            statement.on_conflict_do_update(
                index_elements=[IngestionSourceModel.key],
                set_={
                    "name": statement.excluded.name,
                    "source_type": statement.excluded.source_type,
                    "endpoint_url": statement.excluded.endpoint_url,
                    "parser_name": statement.excluded.parser_name,
                    "content_type": statement.excluded.content_type,
                    "language": statement.excluded.language,
                    "enabled": statement.excluded.enabled,
                    "allowed_domains": statement.excluded.allowed_domains,
                    "poll_interval_seconds": statement.excluded.poll_interval_seconds,
                },
            ).returning(IngestionSourceModel)
        )
        if model is None:
            raise RuntimeError("Unable to save ingestion source.")
        return _registered_source(model)

    async def set_enabled(self, source_id: UUID, enabled: bool) -> bool:
        result = await self._session.execute(
            update(IngestionSourceModel)
            .where(IngestionSourceModel.id == source_id)
            .values(enabled=enabled)
            .returning(IngestionSourceModel.id)
        )
        return result.scalar_one_or_none() is not None


class PostgreSQLIngestionOperationsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_checkpoint(self, source_id: UUID) -> SourceCheckpoint | None:
        model = await self._session.scalar(
            select(IngestionCheckpointModel).where(IngestionCheckpointModel.source_id == source_id)
        )
        if model is None:
            return None
        return SourceCheckpoint(
            source_id=model.source_id,
            etag=model.etag,
            last_modified=model.last_modified,
            last_successful_at=model.last_successful_at,
        )

    async def start_run(self, source_id: UUID, idempotency_key: str) -> RunRecord:
        statement = insert(IngestionRunModel).values(
            source_id=source_id,
            idempotency_key=idempotency_key,
            status=RunStatus.RUNNING,
            started_at=utc_now(),
            attempt_count=1,
        )
        run_id = await self._session.scalar(
            statement.on_conflict_do_update(
                index_elements=[IngestionRunModel.idempotency_key],
                set_={
                    "status": RunStatus.RUNNING,
                    "started_at": utc_now(),
                    "completed_at": None,
                    "attempt_count": IngestionRunModel.attempt_count + 1,
                    "error_code": None,
                    "error_message": None,
                },
                where=IngestionRunModel.status == RunStatus.FAILED,
            ).returning(IngestionRunModel.id)
        )
        model = (
            await self._session.get(IngestionRunModel, run_id)
            if run_id is not None
            else await self._session.scalar(
                select(IngestionRunModel).where(
                    IngestionRunModel.idempotency_key == idempotency_key
                )
            )
        )
        if model is None:
            raise RuntimeError("Unable to create or load ingestion run.")
        return RunRecord(
            id=model.id,
            source_id=model.source_id,
            idempotency_key=model.idempotency_key,
            status=RunStatus(model.status),
            attempt_count=model.attempt_count,
            acquired=run_id is not None,
        )

    async def find_run(self, idempotency_key: str) -> RunRecord | None:
        model = await self._session.scalar(
            select(IngestionRunModel).where(IngestionRunModel.idempotency_key == idempotency_key)
        )
        if model is None:
            return None
        return RunRecord(
            id=model.id,
            source_id=model.source_id,
            idempotency_key=model.idempotency_key,
            status=RunStatus(model.status),
            attempt_count=model.attempt_count,
        )

    async def save_candidates(
        self,
        source_id: UUID,
        run_id: UUID,
        contents: Sequence[NormalizedContent],
        provenance: Sequence[FetchProvenance],
    ) -> int:
        if not contents:
            return 0
        values = [
            {
                "source_id": source_id,
                "run_id": run_id,
                "title": content.title,
                "summary": content.summary,
                "published_at": content.published_at,
                "author": content.author,
                "url": str(content.url),
                "canonical_url": (str(content.canonical_url) if content.canonical_url else None),
                "language": content.language,
                "content_type": content.content_type,
                "tags": list(content.tags),
                "images": [str(image) for image in content.images],
                "content_hash": content.content_hash,
                "provenance": {
                    "source_key": content.source.id,
                    "source_name": content.source.name,
                    "fetches": [
                        {
                            "final_url": fetch.final_url,
                            "fetched_at": fetch.fetched_at.isoformat(),
                            "status_code": fetch.status_code,
                            "etag": fetch.etag,
                            "last_modified": fetch.last_modified,
                        }
                        for fetch in provenance
                    ],
                },
            }
            for content in contents
        ]
        inserted = await self._session.scalars(
            insert(IngestionCandidateModel)
            .values(values)
            .on_conflict_do_nothing(constraint="uq_ingestion_candidates_source_hash")
            .returning(IngestionCandidateModel.id)
        )
        return len(tuple(inserted))

    async def complete_run(
        self,
        run_id: UUID,
        status: RunStatus,
        *,
        item_count: int,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        await self._session.execute(
            update(IngestionRunModel)
            .where(IngestionRunModel.id == run_id)
            .values(
                status=status,
                completed_at=utc_now(),
                item_count=item_count,
                error_code=error_code,
                error_message=error_message,
            )
        )

    async def update_checkpoint(self, checkpoint: SourceCheckpoint) -> None:
        statement = insert(IngestionCheckpointModel).values(
            source_id=checkpoint.source_id,
            etag=checkpoint.etag,
            last_modified=checkpoint.last_modified,
            last_successful_at=checkpoint.last_successful_at,
        )
        await self._session.execute(
            statement.on_conflict_do_update(
                index_elements=[IngestionCheckpointModel.source_id],
                set_={
                    "etag": statement.excluded.etag,
                    "last_modified": statement.excluded.last_modified,
                    "last_successful_at": statement.excluded.last_successful_at,
                },
            )
        )
