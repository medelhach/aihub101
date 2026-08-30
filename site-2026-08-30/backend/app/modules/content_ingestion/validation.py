import re

from app.modules.content_ingestion.exceptions import ContentValidationError
from app.modules.content_ingestion.models import NormalizedContent

_LANGUAGE_PATTERN = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$", re.IGNORECASE)


class DefaultContentValidator:
    def validate(self, content: NormalizedContent) -> None:
        if not content.title.strip():
            raise ContentValidationError("title is required.", details={"field": "title"})
        if not _LANGUAGE_PATTERN.fullmatch(content.language):
            raise ContentValidationError(
                "language must be a valid language tag.",
                details={"field": "language"},
            )
        if len(content.title) > 1_000:
            raise ContentValidationError(
                "title exceeds the maximum length.",
                details={"field": "title"},
            )
        if any(ord(character) < 32 and character not in "\t\n\r" for character in content.title):
            raise ContentValidationError(
                "title contains invalid control characters.",
                details={"field": "title"},
            )
