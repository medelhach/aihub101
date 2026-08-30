from dataclasses import dataclass
from enum import StrEnum


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True, slots=True)
class Sort:
    field: str
    direction: SortDirection = SortDirection.ASC


def parse_sort(value: str, *, allowed_fields: set[str]) -> Sort:
    field, separator, direction = value.partition(":")
    if field not in allowed_fields:
        raise ValueError("Unsupported sort field.")
    return Sort(
        field=field,
        direction=SortDirection(direction) if separator else SortDirection.ASC,
    )
