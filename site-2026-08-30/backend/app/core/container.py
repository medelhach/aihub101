from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.config.settings import Settings
from app.database.session import create_engine, create_session_factory


@dataclass(frozen=True, slots=True)
class AppContainer:
    """Application-scoped dependencies shared by request providers."""

    settings: Settings
    engine: AsyncEngine | None
    session_factory: async_sessionmaker[AsyncSession] | None

    @classmethod
    def build(cls, settings: Settings) -> "AppContainer":
        database_url = settings.database_url.get_secret_value() if settings.database_url else None
        engine = create_engine(
            database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout_seconds,
        )
        return cls(
            settings=settings,
            engine=engine,
            session_factory=create_session_factory(engine),
        )
