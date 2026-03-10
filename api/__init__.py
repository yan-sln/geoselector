"""
API package for geo_selector.
Provides wrappers for external geographic data services.
"""

# Import submodules for convenient access using absolute imports
import importlib, sys
# Ensure core package is available
sys.modules.setdefault('core', importlib.import_module('core'))
# Import submodules
from . import gouvfr, ign

__all__ = ["gouvfr", "ign"]
