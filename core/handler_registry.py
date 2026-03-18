# -*- coding: utf-8 -*-
"""Registry that maps (entity_key, operation) to a callable handler.

The registry is populated from the JSON configuration via ``init``.  Each
handler simply forwards the call to the appropriate ``GeoService`` method.
"""

from __future__ import annotations

from typing import Callable, Dict, Tuple, List, Any

from .service import GeoService
# Importing SelectorImpl would cause a circular import because ``selector`` imports ``HandlerRegistry``.
# Handlers only need an object with ``entity_cls`` and ``service`` attributes, so we use ``Any`` for the type.


class HandlerRegistry:
    _registry: Dict[Tuple[str, str], Callable[[Any, dict], List]] = {}

    @classmethod
    def init(cls, service: GeoService) -> None:
        """Populate the registry from the configuration loaded in ``service``.

        For every entity and every supported operation (search_by_name,
        search_by_code, list_search, search) a small lambda is stored that calls
        the corresponding ``GeoService`` method.
        """
        entities_cfg = service.client.config.get("entities", {})
        for entity_key, cfg in entities_cfg.items():
            for op_name in cfg.keys():
                cls._registry[(entity_key, op_name)] = cls._build_handler(op_name, service)

    @staticmethod
    def _build_handler(operation: str, service: GeoService):
        """Create a handler that forwards the call to the underlying ``ApiClient``.
+
+        The selector builds a ``filters`` dictionary matching the placeholders
+        required by the operation's ``CQL_FILTER``. This generic handler uses the
+        actual operation name (as defined in the configuration) when invoking
+        ``service.client.search``.
+        """
        def handler(selector, filters):
            entity_key = selector.service._entity_key(selector.entity_cls)
            return service.client.search(entity_key, operation, **filters)

        return handler

    @classmethod
    def get(cls, entity_key: str, operation: str):
        return cls._registry.get((entity_key, operation))
