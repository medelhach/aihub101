from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseORMModel


class IngestionSourceModel(BaseORMModel):
    __tablename__ = "ingestion_sources"

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    endpoint_url: Mapped[str] = mapped_column(Text, nullable=False)
    parser_name: Mapped[str] = mapped_column(String(50), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    language: Mapped[str] = mapped_column(String(35), nullable=False, default="en")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allowed_domains: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    poll_interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "poll_interval_seconds >= 60",
            name="ck_ingestion_sources_poll_interval",
        ),
        CheckConstraint(
            "jsonb_array_length(allowed_domains) > 0",
            name="ck_ingestion_sources_allowed_domains",
        ),
        Index("ix_ingestion_sources_enabled", "enabled"),
    )


class IngestionCheckpointModel(BaseORMModel):
    __tablename__ = "ingestion_checkpoints"

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("ingestion_sources.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    etag: Mapped[str | None] = mapped_column(String(512))
    last_modified: Mapped[str | None] = mapped_column(String(512))
    last_successful_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IngestionRunModel(BaseORMModel):
    __tablename__ = "ingestion_runs"

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("ingestion_sources.id", ondelete="CASCADE"), nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'succeeded', 'failed', 'skipped', 'dead_lettered')",
            name="ck_ingestion_runs_status",
        ),
        CheckConstraint(
            "attempt_count > 0 AND item_count >= 0",
            name="ck_ingestion_runs_counts",
        ),
        Index("ix_ingestion_runs_source_started", "source_id", "started_at"),
        Index("ix_ingestion_runs_status", "status"),
    )


class IngestionCandidateModel(BaseORMModel):
    __tablename__ = "ingestion_candidates"

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("ingestion_sources.id", ondelete="CASCADE"), nullable=False
    )
    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("ingestion_runs.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    author: Mapped[str | None] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(35), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    images: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")

    __table_args__ = (
        CheckConstraint(
            "length(content_hash) = 64",
            name="ck_ingestion_candidates_content_hash",
        ),
        UniqueConstraint("source_id", "content_hash", name="uq_ingestion_candidates_source_hash"),
        Index("ix_ingestion_candidates_run", "run_id"),
        Index("ix_ingestion_candidates_status", "status"),
    )
