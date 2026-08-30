from app.core.exceptions import InfrastructureError, ValidationError


class FetchError(InfrastructureError):
    code = "content_fetch_failed"


class ContentTooLargeError(FetchError):
    code = "content_too_large"


class ParseError(ValidationError):
    code = "content_parse_failed"


class ContentValidationError(ValidationError):
    code = "content_validation_failed"
