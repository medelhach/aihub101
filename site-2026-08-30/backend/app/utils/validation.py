import re

from app.core.exceptions import ValidationError

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def require_non_empty(value: str, *, field: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValidationError(f"{field} must not be empty.", details={"field": field})
    return normalized


def validate_slug(value: str) -> str:
    normalized = require_non_empty(value, field="slug").lower()
    if not _SLUG_PATTERN.fullmatch(normalized):
        raise ValidationError(
            "slug must contain lowercase letters, numbers, and single hyphens.",
            details={"field": "slug"},
        )
    return normalized


def require_allowed[T](value: T, *, allowed: set[T], field: str) -> T:
    if value not in allowed:
        raise ValidationError(f"{field} has an unsupported value.", details={"field": field})
    return value
