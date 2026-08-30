from typing import Any

from app.config.settings import Environment, Settings


def settings_factory(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "app_env": Environment.TESTING,
        "app_trusted_hosts": ["testserver"],
        "app_cors_origins": [],
        "database_url": None,
    }
    values.update(overrides)
    return Settings(**values)
