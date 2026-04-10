"""Exception definitions for GeoSelector.

This module defines custom exception classes for API-related errors
and their specific subclasses.
"""

from __future__ import annotations


class ApiError(RuntimeError):
    """Custom exception for API-related errors."""

    # Codes d'erreur spécifiques
    NETWORK_ERROR = "NETWORK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"

    def __init__(
        self,
        message: str,
        url: str | None = None,
        error_code: str | None = None,
        retryable: bool = False,
    ):
        """Initialize the ApiError with an error message and optional URL.

        Parameters
        ----------
        message: str
            Human-readable error description.
        url: str | None, optional
            The request URL that caused the error, if applicable.
        error_code: str | None, optional
            Specific error code for classification.
        retryable: bool, optional
            Whether the error can be retried.
        """
        super().__init__(message)
        self.url = url
        self.error_code = error_code
        self.retryable = retryable

    def to_user_friendly_message(self) -> str:
        """Generate a user-friendly error message."""
        if self.error_code == self.NETWORK_ERROR:
            return "Erreur de connexion réseau. Veuillez vérifier votre connexion internet et réessayer."
        elif self.error_code == self.SERVICE_UNAVAILABLE:
            return "Le service est temporairement indisponible. Veuillez réessayer dans quelques minutes."
        elif self.error_code == self.TIMEOUT_ERROR:
            return "La requête a expiré. Veuillez réessayer."
        else:
            return "Une erreur s'est produite. Veuillez réessayer."


class InvalidSearchParameters(ValueError):
    """Exception raised when search parameters are invalid or insufficient."""

    pass


class MissingRequiredParameter(InvalidSearchParameters):
    """Exception raised when a required parameter for a search operation is missing."""

    def __init__(self, parameter_name: str, operation: str, entity: str):
        self.parameter_name = parameter_name
        self.operation = operation
        self.entity = entity
        message = (
            f"Missing required parameter '{parameter_name}' for {entity}.{operation}"
        )
        super().__init__(message)


class InvalidParameterFormat(InvalidSearchParameters):
    """Exception raised when a parameter has invalid format."""

    def __init__(self, parameter_name: str, expected_format: str, actual_value: str):
        self.parameter_name = parameter_name
        self.expected_format = expected_format
        self.actual_value = actual_value
        message = f"Invalid format for parameter '{parameter_name}': expected {expected_format}, got '{actual_value}'"
        super().__init__(message)


class InsufficientParameters(InvalidSearchParameters):
    """Exception raised when not enough parameters are provided for an operation."""

    def __init__(
        self, operation: str, entity: str, required_count: int, provided_count: int
    ):
        self.operation = operation
        self.entity = entity
        self.required_count = required_count
        self.provided_count = provided_count
        message = f"Insufficient parameters for {entity}.{operation}: required {required_count}, provided {provided_count}"
        super().__init__(message)


class SelectorArgumentError(ValueError):
    """Exception raised when selector methods receive invalid or insufficient arguments."""

    pass


class NetworkError(ApiError):
    """Exception for network-related errors that can be retried."""

    def __init__(self, message: str, url: str | None = None):
        super().__init__(message, url, self.NETWORK_ERROR, retryable=True)


class ValidationError(ApiError):
    """Exception for validation errors that should not be retried."""

    def __init__(self, message: str, url: str | None = None):
        super().__init__(message, url, self.VALIDATION_ERROR, retryable=False)


class ServiceError(ApiError):
    """Exception for service availability errors that can be retried."""

    def __init__(self, message: str, url: str | None = None):
        super().__init__(message, url, self.SERVICE_UNAVAILABLE, retryable=True)


class TimeoutError(ApiError):
    """Exception for timeout errors that can be retried."""

    def __init__(self, message: str, url: str | None = None):
        super().__init__(message, url, self.TIMEOUT_ERROR, retryable=True)
