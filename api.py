"""Proxy module to expose the internal 'api' package as a top-level import.
Allows test code to use `import api.ign` etc.
"""
import importlib, sys
# Load the actual package located at geoselector.api
module = importlib.import_module('geoselector.api')
# Register this module under the name 'api'
sys.modules[__name__] = module
