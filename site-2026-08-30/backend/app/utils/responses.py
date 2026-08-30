from collections.abc import Sequence

from app.schemas.common import PageResponse


def page_response[T](
    items: Sequence[T],
    *,
    next_cursor: str | None = None,
    has_more: bool = False,
    count: int | None = None,
) -> PageResponse[T]:
    return PageResponse[T](
        items=list(items),
        next_cursor=next_cursor,
        has_more=has_more,
        count=count,
    )
