"""add published stories and model catalog

Revision ID: 20260830_0002
Revises: 20260820_0001
Create Date: 2026-08-30
"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260830_0002"
down_revision: str | None = "20260820_0001"
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
        "published_stories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(180), nullable=False),
        sa.Column("section", sa.String(20), nullable=False),
        sa.Column("headline", sa.String(500), nullable=False),
        sa.Column("dek", sa.Text(), nullable=False),
        sa.Column("dateline", sa.String(255), nullable=False),
        sa.Column("lead", sa.Text(), nullable=False),
        sa.Column("sections", postgresql.JSONB(), nullable=False),
        sa.Column("key_facts", postgresql.JSONB(), nullable=False),
        sa.Column("entities", postgresql.JSONB(), nullable=False),
        sa.Column("body_markdown", sa.Text(), nullable=False),
        sa.Column("tags", postgresql.JSONB(), nullable=False),
        sa.Column("source_name", sa.String(255), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("author", sa.String(500), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(35), nullable=False),
        sa.Column("hero_image_url", sa.Text(), nullable=True),
        sa.Column("generation_method", sa.String(50), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=True),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("canonical_url", name="uq_published_stories_canonical_url"),
        sa.ForeignKeyConstraint(
            ["candidate_id"], ["ingestion_candidates.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_published_stories_section_published",
        "published_stories",
        ["section", "published_at"],
    )
    op.create_table(
        "ai_model_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(120), nullable=False),
        sa.Column("family", sa.String(120), nullable=False),
        sa.Column("release_date", sa.String(20), nullable=True),
        sa.Column("modality", sa.String(50), nullable=False),
        sa.Column("context_window_tokens", sa.Integer(), nullable=True),
        sa.Column("max_output_tokens", sa.Integer(), nullable=True),
        sa.Column("parameters", sa.String(120), nullable=True),
        sa.Column("license_name", sa.String(255), nullable=False),
        sa.Column("open_weights", sa.Boolean(), nullable=False),
        sa.Column("availability", sa.String(80), nullable=False),
        sa.Column("input_price_per_million_usd", sa.Float(), nullable=True),
        sa.Column("output_price_per_million_usd", sa.Float(), nullable=True),
        sa.Column("reasoning", sa.Boolean(), nullable=False),
        sa.Column("multimodal", sa.Boolean(), nullable=False),
        sa.Column("fine_tune_available", sa.Boolean(), nullable=False),
        sa.Column("knowledge_cutoff", sa.String(20), nullable=True),
        sa.Column("architecture", sa.Text(), nullable=False),
        sa.Column("deployment_options", postgresql.JSONB(), nullable=False),
        sa.Column("typical_use_cases", postgresql.JSONB(), nullable=False),
        sa.Column("strengths", postgresql.JSONB(), nullable=False),
        sa.Column("limitations", postgresql.JSONB(), nullable=False),
        sa.Column("safety_notes", sa.Text(), nullable=False),
        sa.Column("documentation_url", sa.Text(), nullable=False),
        sa.Column("benchmarks", postgresql.JSONB(), nullable=False),
        sa.Column("pricing_notes", sa.Text(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_ai_model_records_provider", "ai_model_records", ["provider"])
    op.create_index("ix_ai_model_records_modality", "ai_model_records", ["modality"])


def downgrade() -> None:
    op.drop_table("ai_model_records")
    op.drop_table("published_stories")
