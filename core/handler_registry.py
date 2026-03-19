# -*- coding: utf-8 -*-
"""Registry that maps (entity_key, operation) to a callable handler.

The registry is populated from the JSON configuration via ``init``.  Each
handler simply forwards the call to the appropriate ``GeoService`` method.
"""

from __future__ import annotations

from typing import Callable, Dict, Tuple, List, Any

from .service import GeoService
import logging

logger = logging.getLogger(__name__)

# Importing SelectorImpl would cause a circular import because
# ``selector`` imports ``HandlerRegistry``.
# Handlers only need an object with ``entity_cls`` and ``service`` attributes,
# so we use ``Any`` for the type.


class HandlerRegistry:
    _registry: Dict[Tuple[str, str], Callable[[Any, Dict[str, Any]], List[Any]]] = {}

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
                cls._registry[(entity_key, op_name)] = cls._build_handler(
                    op_name, service
                )

    @staticmethod
    def _build_handler(
        operation: str,
        service: GeoService,
    ) -> Callable[[Any, Dict[str, Any]], List[Any]]:
        """Create a handler that returns instantiated entity objects."""

        def handler(selector: Any, filters: Dict[str, Any]) -> List[Any]:
            entity_key = selector.service._entity_key(selector.entity_cls)
            raw = service.client.search(entity_key, operation, **filters)
            return service._instantiate(selector.entity_cls, raw)

        return handler

    @classmethod
    def get(
        cls,
        entity_key: str,
        operation: str,
    ) -> Callable[[Any, Dict[str, Any]], List[Any]] | None:
        return cls._registry.get((entity_key, operation))
