"""
Top-level package for geo_selector.
Provides convenient access to the core service and selector factory.
"""

# Initialize the centralized logging system
from . import logging_config

# Export the main service class and selector factory for convenient imports
from .core.service import GeoService
from .factory.selector_factory import SelectorFactory

# Expose subpackages for legacy absolute imports used in tests
import importlib, sys
# Ensure 'core' is available before importing 'api' to avoid circular import issues
sys.modules.setdefault('core', importlib.import_module('.core', __name__))
sys.modules.setdefault('api', importlib.import_module('.api', __name__))

__all__ = ["GeoService", "SelectorFactory"]
