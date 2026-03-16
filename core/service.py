"""Service layer for GeoSelector.

Provides :class:`GeoService` which orchestrates searches and geometry fetching
using :class:`core.api_client.ApiClient` and the entity classes defined in
:mod:`core.entities`.
"""

from __future__ import annotations

import logging
from typing import List, Type, TypeVar

from .api_client import ApiClient
from .entities import GeoEntity

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=GeoEntity)


class GeoService:
    """High‑level service exposing search and geometry operations.

    Parameters
    ----------
    client:
        An instance of :class:`ApiClient` configured with the appropriate JSON
        configuration.
    """

    def __init__(self, client: ApiClient):
        self.client = client

    # ---------------------------------------------------------------------
    # Search helpers
    # ---------------------------------------------------------------------
    def search_entities(self, entity_cls: Type[T], text: str, limit: int | None = None) -> List[T]:
        """Search for entities of *entity_cls* matching *text*.

        The method decides whether to use ``search_by_name`` or ``search_by_code``
        based on a simple heuristic: if the text looks like a numeric code (or is
        short) we treat it as a code, otherwise as a name.
        """
        entity_key = entity_cls.__name__.lower()
        # Heuristic for operation selection.
        if text.isdigit() or len(text) <= 3:
            mode = "search_by_code"
        else:
            mode = "search_by_name"
        # Some entities (e.g. feuille, parcelle) only have a generic ``search``
        # operation. Fall back to that if the chosen mode is unavailable.
        try:
            raw_features = self.client.search(entity_key, mode, value=text, limit=limit)
        except Exception as exc:  # pragma: no cover – defensive
            logger.error("Search failed for %s with mode %s: %s", entity_key, mode, exc)
            raw_features = []
        results: List[T] = []
        for raw in raw_features:
            try:
                obj = entity_cls.from_api(raw)
                obj.set_service(self)  # type: ignore[arg-type]
                results.append(obj)
            except Exception as exc:  # pragma: no cover – defensive
                logger.error("Failed to instantiate %s from API data: %s", entity_cls.__name__, exc)
        return results

    # ---------------------------------------------------------------------
    # Geometry helpers
    # ---------------------------------------------------------------------
    def fetch_entity_geometry(self, entity_cls: Type[GeoEntity], code: str) -> dict | None:
        """Fetch geometry for a given *entity_cls* identified by *code*.
        """
        entity_key = entity_cls.__name__.lower()
        try:
            geometry = self.client.fetch_geometry(entity_key, value=code)
            return geometry
        except Exception as exc:  # pragma: no cover – defensive
            logger.error("Geometry fetch failed for %s (%s): %s", entity_key, code, exc)
            return None
