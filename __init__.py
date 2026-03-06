"""
Top-level package for geo_selector.
Provides convenient access to the core service and selector factory.
"""

# Export the main service class
from .core.service import GeoService as core_service

# Export the selector factory function
from .factory.selector_factory import SelectorFactory as selector_factory

__all__ = [
    "core_service",
    "selector_factory",
]