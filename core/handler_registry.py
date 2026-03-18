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
            for op in ("search_by_name", "search_by_code", "list_search", "search"):
                if op in cfg:
                    cls._registry[(entity_key, op)] = cls._build_handler(op, service)

    @staticmethod
    def _build_handler(operation: str, service: GeoService):
        if operation == "search_by_name":
            return lambda selector, filters: service.search_by_name(selector.entity_cls, filters["value"])
        if operation == "search_by_code":
            return lambda selector, filters: service.search_by_code(selector.entity_cls, filters["value"])
        if operation == "list_search":
            return lambda selector, filters: service.list_search(selector.entity_cls, **filters)
        if operation == "search":
            return lambda selector, filters: service.list_entities(selector.entity_cls, **filters)
        raise NotImplementedError(f"Unsupported operation '{operation}'")

    @classmethod
    def get(cls, entity_key: str, operation: str):
        return cls._registry.get((entity_key, operation))
