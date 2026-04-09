# -*- coding: utf-8 -*-
"""Selector implementation for GeoSelector.

Provides :class:`SelectorImpl` – a thin wrapper around :class:`core.service.GeoService`
that offers ``select`` and ``get_geometry`` methods – and :class:`SelectorFactory`
which caches service instances per base URL.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Dict, List, Tuple, Type, TypeVar, Optional

from .entities import GeoEntity
from .service import GeoService
from .api_client import ApiClient
from .operation_selector import OperationSelector
from .handler_registry import HandlerRegistry
from .cache import ttl_lru_cache
from .exceptions import ApiError

from ..logging_config import logger

T = TypeVar("T", bound=GeoEntity)

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------


@lru_cache(maxsize=None)
def _extract_placeholders(template: str) -> List[str]:
    """Return all placeholder names found in a CQL template.

    The placeholders are the identifiers wrapped in curly braces, e.g. ``{value}``.
    """
    return re.findall(r"{(\w+)}", template)


def _build_filter(
    operation_cfg: Dict[str, Any],
    args: Tuple[Any, ...],
) -> Dict[str, Any]:
    """Create a filter dictionary for a given operation configuration.

    Supports three calling patterns used throughout the code base:

    1. **Single dict argument** – the dict is returned unchanged.
    2. **Single string argument** – the first placeholder is filled with the string,
       remaining placeholders are set to an empty string.
    3. **Positional arguments** – each argument is mapped to the corresponding
       placeholder in order; missing arguments are filled with an empty string.
    """
    if not args:
        raise ValueError("No arguments provided for filter construction")

    # Case 1: dict supplied directly
    if isinstance(args[0], dict) and len(args) == 1:
        return args[0]

    # Extract placeholders from the operation's CQL_FILTER
    placeholders = _extract_placeholders(operation_cfg.get("CQL_FILTER", ""))
    if not placeholders:
        return {}

    # Case 2: single string – fill first placeholder, rest empty
    if isinstance(args[0], str) and len(args) == 1:
        filters = {placeholders[0]: args[0]}
        for ph in placeholders[1:]:
            filters[ph] = ""
        return filters

    # Case 3: positional arguments – map in order
    filters = {}
    for i, ph in enumerate(placeholders):
        filters[ph] = args[i] if i < len(args) else ""
    return filters


class SelectorImpl:
    """Concrete selector bound to a specific entity class.

    This implementation relies on the new **OperationSelector** to choose the
    appropriate operation and on **HandlerRegistry** to obtain the handler that
    executes the request.
    """

    def __init__(self, entity_cls: Type[T], service: GeoService):
        self.entity_cls = entity_cls
        self.service = service

    @ttl_lru_cache(maxsize=256, ttl=300)
    def select(self, *args: Any, **kwargs: Any) -> List[GeoEntity]:
        """Dispatch a search request using the ``HandlerRegistry``.

        The method now relies on a unified filter builder and a data‑driven
        ``OperationSelector``. Handlers are generated automatically from the JSON
        configuration; missing handlers raise a clear ``NotImplementedError``.
        """
        if not args:
            raise ValueError("select() requires at least one argument")

        # Resolve entity configuration.
        entity_key = self.service._entity_key(self.entity_cls)
        cfg = self.service.client.config.get("entities", {}).get(entity_key, {})

        # Determine the operation using the selector.
        operation = OperationSelector.choose(args, cfg)
        # Log the selection details for debugging and audit purposes.
        logger.debug(
            "SelectorImpl.select called – entity=%s, args=%s, kwargs=%s, chosen_operation=%s",
            self.entity_cls.__name__,
            args,
            kwargs,
            operation,
        )

        # Retrieve the appropriate handler.
        handler = HandlerRegistry.get(entity_key, operation)
        if not handler:
            raise NotImplementedError(
                f"No handler for operation '{operation}' on entity '{entity_key}'"
            )

        # Build filters using the unified helper.
        operation_cfg = cfg.get(operation, {})
        filters = _build_filter(operation_cfg, args)
        # Forward any additional keyword arguments (e.g., limit) to the client.
        if kwargs:
            filters.update(kwargs)

        try:
            return handler(self, filters)
        except ApiError as e:
            # Translate to user-friendly message
            user_message = e.to_user_friendly_message()
            logger.error(f"Error during selection: {user_message}")
            raise ApiError(user_message)

    def get_geometry(self, *args: Any, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Retrieve geometry for the entity.

        * ``*args`` and ``**kwargs`` allow flexible geometry identification.
        * If the first arg is a ``dict`` it is forwarded to the client.
        * A single string argument follows the original behavior.
        * Multiple args map to placeholders via ``_build_filter``.
        """
        logger.debug(
            "SelectorImpl.get_geometry called for %s with args=%s kwargs=%s",
            self.entity_cls.__name__,
            args,
            kwargs,
        )
        # Resolve entity and geometry configuration.
        entity_key = self.service._entity_key(self.entity_cls)
        entity_cfg: Dict[str, Any] = self.service.client.config.get("entities", {}).get(
            entity_key, {}
        )
        geometry_cfg: Dict[str, Any] = entity_cfg.get("geometry", {})
        # If a dict is passed as the first positional argument, forward it.
        if args and isinstance(args[0], dict):
            try:
                return self.service.client.fetch_geometry(entity_key, **args[0])
            except ApiError as e:
                user_message = e.to_user_friendly_message()
                logger.error(f"Error fetching geometry with dict: {user_message}")
                return None

        # If keyword arguments are provided, treat them as filters.
        if kwargs:
            try:
                return self.service.client.fetch_geometry(entity_key, **kwargs)
            except ApiError as e:
                user_message = e.to_user_friendly_message()
                logger.error(f"Error fetching geometry with kwargs: {user_message}")
                return None

        # Ensure at least one positional argument.
        if not args:
            raise ValueError("get_geometry requires at least one argument")

        identifier = args[0]

        # If the identifier looks like a featureId, use it.
        if (
            "featureId" in geometry_cfg
            and isinstance(identifier, str)
            and "." in identifier
        ):
            try:
                return self.service.client.fetch_geometry(
                    entity_key, featureId=identifier
                )
            except ApiError as e:
                user_message = e.to_user_friendly_message()
                logger.error(f"Error fetching geometry with featureId: {user_message}")
                return None

        # No featureId required – if multiple args, build filters and fetch.
        if len(args) > 1:
            filters = _build_filter(geometry_cfg, args)
            try:
                return self.service.client.fetch_geometry(entity_key, **filters)
            except ApiError as e:
                user_message = e.to_user_friendly_message()
                logger.error(f"Error fetching geometry with filters: {user_message}")
                return None

        # Fallback to service helper for simple code lookup.
        try:
            return self.service.fetch_entity_geometry(self.entity_cls, identifier)
        except ApiError as e:
            user_message = e.to_user_friendly_message()
            logger.error(f"Error fetching geometry with fallback: {user_message}")
            return None


class SelectorFactory:
    """Factory that creates :class:`SelectorImpl` instances and caches services.

    The cache is keyed by the ``base_url`` of the underlying ``ApiClient`` so that
    multiple selectors sharing the same WFS endpoint reuse a single ``GeoService``
    (and consequently a single ``ApiClient``).
    """

    _services: Dict[str, GeoService] = {}

    @classmethod
    def create_selector(cls, entity_cls: Type[T]) -> SelectorImpl:
        """Create a selector for *entity_cls*.

        The function loads the default configuration via :class:`ApiClient`,
        re‑uses an existing service for the same ``base_url`` or creates a new one.
        It also ensures that the search handler registry is initialised.
        """
        client = ApiClient()
        base = client.base_url
        if base not in cls._services:
            cls._services[base] = GeoService(client)
            logger.debug("Created new GeoService for base URL %s", base)
        else:
            logger.debug("Reusing existing GeoService for base URL %s", base)
        service = cls._services[base]
        # Initialise the HandlerRegistry (idempotent).
        try:
            HandlerRegistry.init(service)
        except Exception as e:
            logger.error("Failed to initialise handler registry: %s", e)
        return SelectorImpl(entity_cls, service)

    @classmethod
    def reset(cls) -> None:
        """Clear the internal service cache – useful for tests."""
        cls._services.clear()
        logger.debug("SelectorFactory cache cleared")
