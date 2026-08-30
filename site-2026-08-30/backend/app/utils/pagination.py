import base64
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PageRequest:
    limit: int = 20
    cursor: str | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= 100:
            raise ValueError("limit must be between 1 and 100")


def encode_cursor(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode()).decode()


def decode_cursor(value: str) -> str:
    try:
        return base64.urlsafe_b64decode(value.encode()).decode()
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid pagination cursor.") from exc
