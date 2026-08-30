import argparse
import asyncio
import logging

from app.config.settings import get_settings
from app.core.container import AppContainer
from app.core.logging import configure_logging
from app.modules.publishing.service import ContentCycleService


async def run_once() -> None:
    settings = get_settings()
    configure_logging(
        settings.app_log_level,
        service=f"{settings.app_name}-worker",
        environment=settings.app_env,
        version=settings.app_version,
    )
    container = AppContainer.build(settings)
    if container.session_factory is None:
        raise RuntimeError("DATABASE_URL is required for the content cycle worker.")
    try:
        result = await ContentCycleService(settings, container.session_factory).run()
        logging.getLogger("worker").info(
            "content_cycle_complete",
            extra={
                "sources_processed": result.sources_processed,
                "candidates_created": result.candidates_created,
                "stories_published": result.stories_published,
                "stories_skipped": result.stories_skipped,
                "models_seeded": result.models_seeded,
            },
        )
    finally:
        if container.engine is not None:
            await container.engine.dispose()


async def run_loop() -> None:
    settings = get_settings()
    while True:
        try:
            await run_once()
        except Exception:
            logging.getLogger("worker").exception("content_cycle_loop_failed")
        await asyncio.sleep(settings.content_cycle_interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll AI sources and publish structured briefs.")
    parser.add_argument("--once", action="store_true", help="Run a single cycle and exit.")
    args = parser.parse_args()
    asyncio.run(run_once() if args.once else run_loop())


if __name__ == "__main__":
    main()
