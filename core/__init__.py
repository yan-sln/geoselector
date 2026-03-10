"""
Core package for geo_selector.
Provides entities, service, selector and related utilities.
"""

# Export core classes for convenient import
from .service import GeoService
from .selector import EntitySelector, EntitySelectorImpl

__all__ = [
    "GeoService",
    "EntitySelector",
    "EntitySelectorImpl",
]
