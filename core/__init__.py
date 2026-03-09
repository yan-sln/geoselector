"""
Core package for geo_selector.
Provides entities, service, selector and related utilities.
"""

# Core package exports are intentionally lazy to avoid circular imports.
# Users can import needed classes directly, e.g.:
#   from core.service import GeoService
#   from core.selector import EntitySelector, EntitySelectorImpl


__all__ = [
    "GeoService",
    "EntitySelector",
    "EntitySelectorImpl",
]