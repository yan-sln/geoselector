"""Custom exception hierarchy for the geoselector package.

All exceptions inherit from :class:`MyGeoselectorError` so that callers can
catch a single base class if they wish.  The concrete subclasses provide more
specific error information.
"""

class MyGeoselectorError(Exception):
    """Base class for all custom exceptions of the package."""
    pass


class InvalidEntityTypeError(MyGeoselectorError):
    """Raised when the caller asks for a type not covered by the API."""
    def __init__(self, entity_type: str):
        super().__init__(f"Type d'entité non supporté : {entity_type!r}")
        self.entity_type = entity_type


class GeoApiError(MyGeoselectorError):
    """Wraps low‑level HTTP / JSON errors coming from the external API."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class EntityNotFoundError(MyGeoselectorError):
    """Raised when a search returns no result."""
    def __init__(self, entity_type: str, query: str):
        super().__init__(f"Aucune entité trouvée pour « {query} » ({entity_type})")
        self.entity_type = entity_type
        self.query = query

# Export public API for core exceptions
__all__ = [
    "MyGeoselectorError",
    "InvalidEntityTypeError",
    "GeoApiError",
    "EntityNotFoundError",
]