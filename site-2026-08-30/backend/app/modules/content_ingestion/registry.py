from uuid import UUID

from app.modules.content_ingestion.interfaces import SourceRegistryRepository, URLGuard
from app.modules.content_ingestion.operations import RegisteredSource


class SourceRegistry:
    def __init__(
        self,
        repository: SourceRegistryRepository,
        url_guard: URLGuard,
    ) -> None:
        self._repository = repository
        self._url_guard = url_guard

    async def register(self, source: RegisteredSource) -> RegisteredSource:
        if not source.key or source.poll_interval_seconds < 60:
            raise ValueError(
                "Source key is required and polling interval must be at least 60 seconds."
            )
        await self._url_guard.validate(source.endpoint_url, source.allowed_domains)
        return await self._repository.save(source)

    async def enable(self, source_id: UUID) -> bool:
        return await self._repository.set_enabled(source_id, True)

    async def disable(self, source_id: UUID) -> bool:
        return await self._repository.set_enabled(source_id, False)
