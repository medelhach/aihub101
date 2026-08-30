from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.content_ingestion.persistence.repositories import (
    PostgreSQLIngestionOperationsRepository,
    PostgreSQLSourceRegistryRepository,
)


class PostgreSQLIngestionUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self.sources: PostgreSQLSourceRegistryRepository
        self.operations: PostgreSQLIngestionOperationsRepository

    async def __aenter__(self) -> "PostgreSQLIngestionUnitOfWork":
        self._session = self._session_factory()
        await self._session.begin()
        self.sources = PostgreSQLSourceRegistryRepository(self._session)
        self.operations = PostgreSQLIngestionOperationsRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc_type is None:
                await self._session.commit()
            else:
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None
