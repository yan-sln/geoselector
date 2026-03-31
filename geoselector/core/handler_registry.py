# -*- coding: utf-8 -*-
"""Registry that maps (entity_key, operation) to a callable handler.

The registry is populated from the JSON configuration via ``init``.  Each
handler simply forwards the call to the appropriate ``GeoService`` method.
"""

from __future__ import annotations

from typing import Callable, Dict, Tuple, List, Any

from .service import GeoService
import logging

from ..logging_config import logger

# Importing SelectorImpl would cause a circular import because
# ``selector`` imports ``HandlerRegistry``.
# Handlers only need an object with ``entity_cls`` and ``service`` attributes,
# so we use ``Any`` for the type.


class HandlerRegistry:
    """Registry mapping entity/operation pairs to handler callables.

    The registry is a class‑level dictionary where each key is a tuple of
    ``(entity_key, operation)`` and the value is a callable that, given a selector
    and a filter dictionary, returns a list of instantiated entity objects.
    Handlers are populated via :meth:`init` based on the service configuration.
    """

    _registry: Dict[Tuple[str, str], Callable[[Any, Dict[str, Any]], List[Any]]] = {}

    @classmethod
    def init(cls, service: GeoService) -> None:
        """Initialize the handler registry.

        Parameters
        ----------
        service: GeoService
            The service instance providing access to the API client and configuration.

        The method reads the ``entities`` section of the configuration loaded in ``service``.
        For each entity and each supported operation (e.g., ``search_by_name``, ``search_by_code``,
        ``list_search``, ``search``) it registers a handler lambda that forwards calls to the
        appropriate ``GeoService`` method. These handlers are stored in the class‑level ``_registry``
        dictionary keyed by ``(entity_key, operation)``.
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
        """Create a handler callable for a specific operation.

        Parameters
        ----------
        operation: str
            The operation name (e.g., ``search_by_name``) as defined in the
            configuration for the entity.
        service: GeoService
            The service instance used to perform the underlying API request.

        Returns
        -------
        Callable[[Any, Dict[str, Any]], List[Any]]
            A function that accepts a selector (providing ``entity_cls``) and a
            dictionary of filter arguments, performs the appropriate search via
            ``service.client.search`` and returns a list of instantiated entity
            objects.
        """

        def handler(selector: Any, filters: Dict[str, Any]) -> List[Any]:
            entity_key = selector.service._entity_key(selector.entity_cls)
            # Log the handler invocation details.
            logger.info(
                "Handler invoked – entity_key=%s, operation=%s, filters=%s",
                entity_key,
                operation,
                filters,
            )
            raw = service.client.search(entity_key, operation, **filters)
            return service._instantiate(selector.entity_cls, raw)

        return handler

    @classmethod
    def get(
        cls,
        entity_key: str,
        operation: str,
    ) -> Callable[[Any, Dict[str, Any]], List[Any]] | None:
        """Retrieve the handler callable for a given entity and operation.

        Parameters
        ----------
        entity_key: str
            The key identifying the entity type (e.g., "country").
        operation: str
            The operation name as defined in the configuration (e.g., "search_by_name").

        Returns
        -------
        Callable[[Any, Dict[str, Any]], List[Any]] | None
            The handler function that takes a selector and filter dict and returns a list of instantiated entities, or ``None`` if no handler is registered for the given pair.
        """
        return cls._registry.get((entity_key, operation))
