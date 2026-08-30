from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.main import create_application
from tests.factories import settings_factory


@pytest.fixture
def settings() -> Settings:
    return settings_factory()


@pytest.fixture
def application(settings: Settings) -> FastAPI:
    return create_application(settings)


@pytest.fixture
def client(application: FastAPI) -> Iterator[TestClient]:
    with TestClient(application) as test_client:
        yield test_client
