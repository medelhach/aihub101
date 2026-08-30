from pydantic import BaseModel, Field

from app.config.settings import Settings


class IngestionConfig(BaseModel):
    timeout_seconds: float = Field(default=15.0, gt=0, le=120)
    retries: int = Field(default=3, ge=0, le=10)
    rate_limit_per_minute: int = Field(default=60, ge=1, le=10_000)
    enabled_sources: frozenset[str] = frozenset()
    disabled_sources: frozenset[str] = frozenset()
    user_agent: str = Field(default="AI-Intelligence-Hub/0.1", min_length=1, max_length=256)
    maximum_article_size_bytes: int = Field(default=5 * 1024 * 1024, ge=1024, le=100 * 1024 * 1024)

    def is_source_enabled(self, source_id: str) -> bool:
        if source_id in self.disabled_sources:
            return False
        return not self.enabled_sources or source_id in self.enabled_sources

    @classmethod
    def from_settings(cls, settings: Settings) -> "IngestionConfig":
        return cls(
            timeout_seconds=settings.content_ingestion_timeout_seconds,
            retries=settings.content_ingestion_retries,
            rate_limit_per_minute=settings.content_ingestion_rate_limit_per_minute,
            enabled_sources=frozenset(settings.content_ingestion_enabled_sources),
            disabled_sources=frozenset(settings.content_ingestion_disabled_sources),
            user_agent=settings.content_ingestion_user_agent,
            maximum_article_size_bytes=settings.content_ingestion_maximum_article_size_bytes,
        )
