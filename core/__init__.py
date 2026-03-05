# Export public API for the core package
from .geo_service import GeoDataService
from .entities import GeoEntity, Municipality, Department, Region
from .exceptions import MyGeoselectorError, InvalidEntityTypeError, GeoApiError, EntityNotFoundError

__all__ = [
    "GeoDataService",
    "GeoEntity",
    "Municipality",
    "Department",
    "Region",
    "MyGeoselectorError",
    "InvalidEntityTypeError",
    "GeoApiError",
    "EntityNotFoundError",
]