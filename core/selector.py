"""Selector implementation for GeoSelector.

Provides :class:`SelectorImpl` – a thin wrapper around :class:`core.service.GeoService`
that offers ``select`` and ``get_geometry`` methods – and :class:`SelectorFactory`
which caches service instances per base URL.
"""

from __future__ import annotations

import logging
from typing import List, Type, TypeVar, Dict

from .entities import GeoEntity
from .service import GeoService
from .api_client import ApiClient

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=GeoEntity)


class SelectorImpl:
    """Concrete selector bound to a specific entity class.

    Parameters
    ----------
    entity_cls:
        The concrete :class:`GeoEntity` subclass this selector works with.
    service:
        An instance of :class:`GeoService` used to perform the actual queries.
    """

    def __init__(self, entity_cls: Type[T], service: GeoService):
        self.entity_cls = entity_cls
        self.service = service

    def select(self, text: str) -> List[GeoEntity]:
        """Search for entities matching *text*.

        Delegates to :meth:`GeoService.search_entities`.
        """
        logger.debug("SelectorImpl.select called for %s with text %s", self.entity_cls.__name__, text)
        return self.service.search_entities(self.entity_cls, text)

    def get_geometry(self, code: str) -> dict | None:
        """Retrieve geometry for the entity identified by *code*.
        """
        logger.debug("SelectorImpl.get_geometry called for %s with code %s", self.entity_cls.__name__, code)
        return self.service.fetch_entity_geometry(self.entity_cls, code)


class SelectorFactory:
    """Factory that creates :class:`SelectorImpl` instances.

    It maintains a cache of :class:`GeoService` objects keyed by the ``base_url``
    from the configuration, ensuring that multiple selectors for the same data
    source share a single service (and thus a single :class:`ApiClient`).
    """

    _services: Dict[str, GeoService] = {}

    @classmethod
    def create_selector(cls, entity_cls: Type[T]) -> SelectorImpl:
        """Create a selector for *entity_cls*.

        The function loads the default configuration file, re‑uses an existing
        service for the same ``base_url`` or creates a new one.
        """
        # Load configuration via ApiClient (default path).
        client = ApiClient()
        base = client.base_url
        if base not in cls._services:
            cls._services[base] = GeoService(client)
            logger.debug("Created new GeoService for base URL %s", base)
        else:
            logger.debug("Reusing existing GeoService for base URL %s", base)
        service = cls._services[base]
        return SelectorImpl(entity_cls, service)

    @classmethod
    def reset(cls) -> None:
        """Clear the internal service cache – useful for tests.
        """
        cls._services.clear()
        logger.debug("SelectorFactory cache cleared")
