from enum import StrEnum
from functools import lru_cache

from pydantic import AnyHttpUrl, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Validated application configuration loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "AI Intelligence Hub API"
    app_version: str = "0.1.0"
    app_env: Environment = Environment.DEVELOPMENT
    app_debug: bool = False
    app_log_level: LogLevel = LogLevel.INFO
    app_docs_enabled: bool = True
    app_cors_origins: list[AnyHttpUrl] = Field(
        default_factory=lambda: [AnyHttpUrl("http://localhost:3000")]
    )
    app_trusted_hosts: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    app_gzip_minimum_size: int = Field(default=1000, ge=256)
    app_frontend_url: AnyHttpUrl = AnyHttpUrl("http://localhost:3000")
    app_backend_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    database_url: SecretStr | None = None
    database_pool_size: int = Field(default=10, ge=1, le=100)
    database_max_overflow: int = Field(default=20, ge=0, le=100)
    database_pool_timeout_seconds: int = Field(default=30, ge=1, le=300)

    content_ingestion_timeout_seconds: float = Field(default=15.0, gt=0, le=120)
    content_ingestion_retries: int = Field(default=3, ge=0, le=10)
    content_ingestion_rate_limit_per_minute: int = Field(default=60, ge=1, le=10_000)
    content_ingestion_enabled_sources: list[str] = Field(default_factory=list)
    content_ingestion_disabled_sources: list[str] = Field(default_factory=list)
    content_ingestion_user_agent: str = (
        "Mozilla/5.0 (compatible; AI-Intelligence-Hub/0.1; +https://localhost:3000)"
    )
    content_ingestion_maximum_article_size_bytes: int = Field(
        default=5 * 1024 * 1024, ge=1024, le=100 * 1024 * 1024
    )
    content_cycle_secret: SecretStr | None = None
    publishing_max_candidates_per_cycle: int = Field(default=40, ge=1, le=200)
    content_cycle_interval_seconds: int = Field(default=900, ge=60, le=86_400)

    azure_openai_endpoint: AnyHttpUrl | None = None
    azure_openai_api_key: SecretStr | None = None
    azure_openai_api_version: str | None = None
    azure_openai_deployment: str | None = None
    azure_storage_connection_string: SecretStr | None = None
    azure_storage_container_name: str | None = None
    azure_key_vault_url: AnyHttpUrl | None = None

    jwt_secret_key: SecretStr | None = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    @model_validator(mode="after")
    def validate_environment(self) -> "Settings":
        if self.app_env is Environment.PRODUCTION:
            if self.app_debug:
                raise ValueError("APP_DEBUG must be false in production")
            if self.database_url is None:
                raise ValueError("DATABASE_URL is required in production")
            if "*" in self.app_trusted_hosts:
                raise ValueError("Wildcard trusted hosts are forbidden in production")
            if self.content_cycle_secret is None:
                raise ValueError("CONTENT_CYCLE_SECRET is required in production")
        return self

    @property
    def is_testing(self) -> bool:
        return self.app_env is Environment.TESTING


@lru_cache
def get_settings() -> Settings:
    return Settings()
