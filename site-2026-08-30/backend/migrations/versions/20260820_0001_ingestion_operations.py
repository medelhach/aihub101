"""add ingestion operations tables

Revision ID: 20260820_0001
Revises:
Create Date: 2026-08-20
"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260820_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> tuple[sa.Column[Any], sa.Column[Any]]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def upgrade() -> None:
    op.create_table(
        "ingestion_sources",
        sa.Column(
            "id",
            sa.Uuid(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("endpoint_url", sa.Text(), nullable=False),
        sa.Column("parser_name", sa.String(50), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("language", sa.String(35), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("allowed_domains", postgresql.JSONB(), nullable=False),
        sa.Column("poll_interval_seconds", sa.Integer(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "poll_interval_seconds >= 60",
            name="ck_ingestion_sources_poll_interval",
        ),
        sa.CheckConstraint(
            "jsonb_array_length(allowed_domains) > 0",
            name="ck_ingestion_sources_allowed_domains",
        ),
        sa.UniqueConstraint("key"),
    )
    op.create_index("ix_ingestion_sources_enabled", "ingestion_sources", ["enabled"])

    op.create_table(
        "ingestion_checkpoints",
        sa.Column(
            "id",
            sa.Uuid(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "source_id",
            sa.Uuid(),
            sa.ForeignKey("ingestion_sources.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("etag", sa.String(512)),
        sa.Column("last_modified", sa.String(512)),
        sa.Column("last_successful_at", sa.DateTime(timezone=True)),
        *timestamp_columns(),
    )

    op.create_table(
        "ingestion_runs",
        sa.Column(
            "id",
            sa.Uuid(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "source_id",
            sa.Uuid(),
            sa.ForeignKey("ingestion_sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("idempotency_key", sa.String(255), nullable=False, unique=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(100)),
        sa.Column("error_message", sa.Text()),
        *timestamp_columns(),
        sa.CheckConstraint(
            "status IN ('running', 'succeeded', 'failed', 'skipped', 'dead_lettered')",
            name="ck_ingestion_runs_status",
        ),
        sa.CheckConstraint(
            "attempt_count > 0 AND item_count >= 0",
            name="ck_ingestion_runs_counts",
        ),
    )
    op.create_index(
        "ix_ingestion_runs_source_started",
        "ingestion_runs",
        ["source_id", "started_at"],
    )
    op.create_index("ix_ingestion_runs_status", "ingestion_runs", ["status"])

    op.create_table(
        "ingestion_candidates",
        sa.Column(
            "id",
            sa.Uuid(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "source_id",
            sa.Uuid(),
            sa.ForeignKey("ingestion_sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "run_id",
            sa.Uuid(),
            sa.ForeignKey("ingestion_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("author", sa.String(500)),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("canonical_url", sa.Text()),
        sa.Column("language", sa.String(35), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("tags", postgresql.JSONB(), nullable=False),
        sa.Column("images", postgresql.JSONB(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("provenance", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "length(content_hash) = 64",
            name="ck_ingestion_candidates_content_hash",
        ),
        sa.UniqueConstraint(
            "source_id",
            "content_hash",
            name="uq_ingestion_candidates_source_hash",
        ),
    )
    op.create_index("ix_ingestion_candidates_run", "ingestion_candidates", ["run_id"])
    op.create_index("ix_ingestion_candidates_status", "ingestion_candidates", ["status"])


def downgrade() -> None:
    op.drop_table("ingestion_candidates")
    op.drop_table("ingestion_runs")
    op.drop_table("ingestion_checkpoints")
    op.drop_table("ingestion_sources")
