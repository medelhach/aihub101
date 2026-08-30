from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
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


class PublishedStoryModel(BaseORMModel):
    __tablename__ = "published_stories"

    slug: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    section: Mapped[str] = mapped_column(String(20), nullable=False)
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    dek: Mapped[str] = mapped_column(Text, nullable=False)
    dateline: Mapped[str] = mapped_column(String(255), nullable=False)
    lead: Mapped[str] = mapped_column(Text, nullable=False)
    sections: Mapped[list[dict[str, str]]] = mapped_column(JSONB, nullable=False)
    key_facts: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    entities: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    body_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str | None] = mapped_column(String(500))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(35), nullable=False, default="en")
    hero_image_url: Mapped[str | None] = mapped_column(Text)
    generation_method: Mapped[str] = mapped_column(String(50), nullable=False)
    candidate_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ingestion_candidates.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("canonical_url", name="uq_published_stories_canonical_url"),
        Index("ix_published_stories_section_published", "section", "published_at"),
    )


class AIModelRecordModel(BaseORMModel):
    __tablename__ = "ai_model_records"

    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    family: Mapped[str] = mapped_column(String(120), nullable=False)
    release_date: Mapped[str | None] = mapped_column(String(20))
    modality: Mapped[str] = mapped_column(String(50), nullable=False)
    context_window_tokens: Mapped[int | None] = mapped_column(Integer)
    max_output_tokens: Mapped[int | None] = mapped_column(Integer)
    parameters: Mapped[str | None] = mapped_column(String(120))
    license_name: Mapped[str] = mapped_column(String(255), nullable=False)
    open_weights: Mapped[bool] = mapped_column(Boolean, nullable=False)
    availability: Mapped[str] = mapped_column(String(80), nullable=False)
    input_price_per_million_usd: Mapped[float | None] = mapped_column(Float)
    output_price_per_million_usd: Mapped[float | None] = mapped_column(Float)
    reasoning: Mapped[bool] = mapped_column(Boolean, nullable=False)
    multimodal: Mapped[bool] = mapped_column(Boolean, nullable=False)
    fine_tune_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    knowledge_cutoff: Mapped[str | None] = mapped_column(String(20))
    architecture: Mapped[str] = mapped_column(Text, nullable=False)
    deployment_options: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    typical_use_cases: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    strengths: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    limitations: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    safety_notes: Mapped[str] = mapped_column(Text, nullable=False)
    documentation_url: Mapped[str] = mapped_column(Text, nullable=False)
    benchmarks: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    pricing_notes: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("ix_ai_model_records_provider", "provider"),
        Index("ix_ai_model_records_modality", "modality"),
    )
