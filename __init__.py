"""
Top-level package for geo_selector.
Provides convenient access to the core service and selector factory.
"""

# Initialize the centralized logging system
from . import logging_config

# Export the main service class

# Export the selector factory function

# Expose subpackages for legacy absolute imports used in tests
import importlib, sys
sys.modules['api'] = importlib.import_module('.api', __name__)
# core is already importable as a top-level package, but ensure alias as well
sys.modules['core'] = importlib.import_module('.core', __name__)

__all__ = []
