from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository[RepositoryEntity]:
    """Base for repositories; concrete repositories expose use-case-specific methods."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
