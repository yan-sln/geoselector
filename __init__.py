"""
Top-level package for geo_selector.
Provides convenient access to the core service and selector factory.
"""

# Initialise le système de logging centralisé
from . import logging_config

# Export the main service class
from .core.service import GeoService as core_service

# Export the selector factory function
from .factory.selector_factory import SelectorFactory as selector_factory

# Expose subpackages for legacy absolute imports used in tests
import importlib, sys
sys.modules['api'] = importlib.import_module('.api', __name__)
# core is already importable as a top-level package, but ensure alias as well
sys.modules['core'] = importlib.import_module('.core', __name__)

__all__ = [
    "core_service",
    "selector_factory",
]
