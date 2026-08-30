from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str


class PageResponse[T](BaseModel):
    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False
    count: int | None = Field(default=None, ge=0)
