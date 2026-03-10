import importlib, sys
_module = importlib.import_module('geoselector.api')
sys.modules[__name__] = _module
