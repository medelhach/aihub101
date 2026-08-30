from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError as PydanticValidationError

from app.config.settings import Environment, Settings
from app.core.exceptions import BusinessError
from app.utils.datetime import ensure_utc
from app.utils.pagination import PageRequest, decode_cursor, encode_cursor
from app.utils.responses import page_response
from app.utils.sorting import SortDirection, parse_sort
from app.utils.validation import validate_slug


def test_production_settings_require_database() -> None:
    with pytest.raises(PydanticValidationError):
        Settings(app_env=Environment.PRODUCTION, database_url=None)


def test_invalid_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/api/v1/health/live", headers={"X-Request-ID": "invalid"})
    UUID(response.headers["X-Request-ID"])


def test_application_errors_use_standard_envelope(application: FastAPI) -> None:
    async def raise_error() -> None:
        raise BusinessError("Conflict.")

    application.add_api_route("/test-error", raise_error)
    with TestClient(application) as test_client:
        response = test_client.get("/test-error")

    assert response.status_code == 409
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "business_rule_violation"
    assert response.json()["correlation_id"]


def test_http_errors_use_standard_envelope(client: TestClient) -> None:
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.json()["code"] == "http_error"


def test_common_validation_and_pagination_helpers() -> None:
    assert validate_slug("core-platform") == "core-platform"
    cursor = encode_cursor("stable-value")
    assert decode_cursor(cursor) == "stable-value"
    assert PageRequest(limit=100).limit == 100
    assert page_response(["item"], has_more=False).items == ["item"]
    assert parse_sort("created_at:desc", allowed_fields={"created_at"}).direction is (
        SortDirection.DESC
    )


def test_datetime_helper_requires_timezone() -> None:
    aware = datetime.now(UTC)
    assert ensure_utc(aware + timedelta(hours=1)).tzinfo is UTC
    with pytest.raises(ValueError):
        ensure_utc(datetime.now())
