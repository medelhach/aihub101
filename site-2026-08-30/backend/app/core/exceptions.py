from typing import Any


class AppError(Exception):
    code = "application_error"
    status_code = 500

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationError(AppError):
    code = "validation_error"
    status_code = 422


class BusinessError(AppError):
    code = "business_rule_violation"
    status_code = 409


class InfrastructureError(AppError):
    code = "infrastructure_error"
    status_code = 503


class NotFoundError(AppError):
    code = "not_found"
    status_code = 404
