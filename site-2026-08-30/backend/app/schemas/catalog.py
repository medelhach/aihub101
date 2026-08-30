from datetime import datetime

from pydantic import BaseModel, Field


class StorySectionResponse(BaseModel):
    heading: str
    body: str


class StorySummaryResponse(BaseModel):
    slug: str
    section: str
    headline: str
    dek: str
    dateline: str
    source_name: str
    source_url: str
    author: str | None
    published_at: datetime | None
    word_count: int
    tags: list[str]
    hero_image_url: str | None
    generation_method: str


class StoryDetailResponse(StorySummaryResponse):
    lead: str
    sections: list[StorySectionResponse]
    key_facts: list[str]
    entities: list[str]
    body_markdown: str
    canonical_url: str
    language: str


class CycleResponse(BaseModel):
    sources_processed: int
    candidates_created: int
    stories_published: int
    stories_skipped: int
    models_seeded: int
    details: dict[str, object]


class ModelSummaryResponse(BaseModel):
    slug: str
    name: str
    provider: str
    family: str
    release_date: str | None
    modality: str
    context_window_tokens: int | None
    open_weights: bool
    reasoning: bool
    multimodal: bool
    input_price_per_million_usd: float | None
    output_price_per_million_usd: float | None
    license_name: str
    availability: str


class ModelDetailResponse(ModelSummaryResponse):
    max_output_tokens: int | None
    parameters: str | None
    fine_tune_available: bool
    knowledge_cutoff: str | None
    architecture: str
    deployment_options: list[str]
    typical_use_cases: list[str]
    strengths: list[str]
    limitations: list[str]
    safety_notes: str
    documentation_url: str
    benchmarks: dict[str, object]
    pricing_notes: str
    id: str


class ComparisonRowResponse(BaseModel):
    key: str
    label: str
    description: str
    values: list[str]
    differs: bool


class ComparisonSummaryResponse(BaseModel):
    model_count: int
    open_weights_count: int
    reasoning_count: int
    multimodal_count: int
    cheapest_input: str | None
    largest_context: str | None


class ComparisonResponse(BaseModel):
    models: list[ModelDetailResponse]
    rows: list[ComparisonRowResponse]
    summary: ComparisonSummaryResponse


class CompareQuery(BaseModel):
    slugs: list[str] = Field(min_length=2, max_length=6)
