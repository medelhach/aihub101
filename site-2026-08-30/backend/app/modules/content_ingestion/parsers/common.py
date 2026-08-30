from app.modules.content_ingestion.exceptions import ParseError
from app.modules.content_ingestion.models import FetchedContent


def decode_body(content: FetchedContent) -> str:
    try:
        return content.body.decode(content.encoding)
    except (LookupError, UnicodeDecodeError) as exc:
        raise ParseError(
            "Content encoding is invalid.",
            details={"encoding": content.encoding},
        ) from exc
