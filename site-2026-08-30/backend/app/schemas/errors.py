from typing import Any

from pydantic import BaseModel


class ProblemDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    correlation_id: str | None = None
    errors: dict[str, Any] | list[dict[str, Any]] | None = None
