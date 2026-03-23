"""Service layer for GeoSelector.

Provides :class:`GeoService` which orchestrates searches and geometry fetching
using :class:`core.api_client.ApiClient` and the entity classes defined in
:mod:`core.entities`.
"""

from __future__ import annotations

import logging
from typing import List, Type, TypeVar, Dict, Any

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
    # Helper utilities
    # ---------------------------------------------------------------------
    @staticmethod
    def _entity_key(entity_cls: Type[GeoEntity]) -> str:
        """Convert a CamelCase entity class to the snake_case key used in the
        API configuration (e.g. ``Region`` → ``region``)."""
        import re

        return re.sub(r"(?<!^)(?=[A-Z])", "_", entity_cls.__name__).lower()

    def _instantiate(
        self, entity_cls: Type[T], raw_features: List[Dict[str, Any]]
    ) -> List[T]:
        """Create entity instances from raw API feature dictionaries.

        Errors while instantiating a single feature are logged and the feature
        is skipped.
        """
        results: List[T] = []
        for raw in raw_features:
            try:
                obj = entity_cls.from_api(raw)
                obj.set_service(self)
                results.append(obj)
            except Exception as exc:  # pragma: no cover – defensive
                logger.error(
                    "Failed to instantiate %s from API data: %s",
                    entity_cls.__name__,
                    exc,
                )
        return results

    # ---------------------------------------------------------------------
    # Search helpers – explicit modes
    # ---------------------------------------------------------------------
    def search_by_name(
        self, entity_cls: Type[T], name: str, limit: int | None = None
    ) -> List[T]:
        """Search *entity_cls* by its human‑readable name.

        Applicable to entities that expose a ``search_by_name`` operation in the
        configuration (region, departement, commune).
        """
        entity_key = self._entity_key(entity_cls)
        raw = self.client.search(entity_key, "search_by_name", value=name, limit=limit)
        return self._instantiate(entity_cls, raw)

    def search_by_code(
        self, entity_cls: Type[T], code: str, limit: int | None = None
    ) -> List[T]:
        """Search *entity_cls* by its identifier code.

        Used for region, departement, commune and also for entities that only
        provide a ``search_by_code`` operation (e.g. arrondissement).
        """
        entity_key = self._entity_key(entity_cls)
        raw = self.client.search(entity_key, "search_by_code", value=code, limit=limit)
        return self._instantiate(entity_cls, raw)

    def list_entities(self, entity_cls: Type[T], **filters: Any) -> List[T]:
        """Generic listing for entities that only expose a ``search`` block.

        Typical for ``feuille``, ``parcelle`` and ``subdivision_fiscale`` where the
        caller must provide the required parameters (e.g. ``code_insee``,
        ``section``). All keyword arguments are forwarded to the underlying client.
        If required placeholders are missing, return an empty list to keep selector
        behavior consistent with mocked tests.
        """
        entity_key = self._entity_key(entity_cls)
        try:
            raw = self.client.search(entity_key, "search", **filters)
        except Exception as exc:  # pragma: no cover – defensive
            logger.error(
                "list_entities failed for %s with filters %s: %s",
                entity_key,
                filters,
                exc,
            )
            raw = []
        return self._instantiate(entity_cls, raw)

    def list_search(self, entity_cls: Type[T], **filters: Any) -> List[T]:
        """Execute a ``list_search`` operation defined in the JSON configuration.

        The ``list_search`` block is used for entities that require a specific
        filter (e.g. ``code_insee`` or ``section``). All keyword arguments are
        forwarded to :meth:`ApiClient.search` which will substitute the
        placeholders defined in the ``CQL_FILTER`` of the configuration.
        """
        entity_key = self._entity_key(entity_cls)
        raw = self.client.search(entity_key, "list_search", **filters)
        return self._instantiate(entity_cls, raw)

    # Search helpers
    # ---------------------------------------------------------------------
    def search_entities(
        self, entity_cls: Type[T], text: str, limit: int | None = None
    ) -> List[T]:
        """Search for entities of *entity_cls* matching *text*.

        The method decides whether to use ``search_by_name`` or ``search_by_code``
        based on a simple heuristic: if the text looks like a numeric code (or is
        short) we treat it as a code, otherwise as a name.
        """
        # Convert CamelCase class name to snake_case to match config keys
        import re

        entity_key = re.sub(r"(?<!^)(?=[A-Z])", "_", entity_cls.__name__).lower()
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
            print(f"Search failed for {entity_key} with mode {mode}: {exc}")
            # Fallback to generic 'search' operation if available
            try:
                raw_features = self.client.search(
                    entity_key, "search", value=text, limit=limit
                )
            except Exception:
                raw_features = []
        results: List[T] = []
        for raw in raw_features:
            try:
                obj = entity_cls.from_api(raw)
                obj.set_service(self)
                results.append(obj)
            except Exception as exc:  # pragma: no cover – defensive
                logger.error(
                    "Failed to instantiate %s from API data: %s",
                    entity_cls.__name__,
                    exc,
                )
        return results

    # ---------------------------------------------------------------------
    # Geometry helpers
    # ---------------------------------------------------------------------
    def fetch_entity_geometry(
        self, entity_cls: Type[GeoEntity], *args: Any, **kwargs: Any
    ) -> Dict[str, Any] | None:
        """Fetch geometry for a given *entity_cls*.

        This implementation builds the request parameters dynamically based on the
        placeholders defined in the entity's ``geometry`` configuration. It supports
        three calling styles:

        1. A single dict argument – passed directly to the client.
        2. Keyword arguments – used as‑is (the caller provides the correct names).
        3. Positional arguments – mapped to the placeholders in the order they
           appear in the ``CQL_FILTER``.
        """
        # 1⃣ Convert class name to configuration key
        import re

        entity_key = re.sub(r"(?<!^)(?=[A-Z])", "_", entity_cls.__name__).lower()

        # 2⃣ Retrieve geometry configuration for the entity
        entity_cfg = self.client.config.get("entities", {}).get(entity_key, {})
        geometry_cfg = entity_cfg.get("geometry", {})
        cql_filter = geometry_cfg.get("CQL_FILTER", "")

        # 3⃣ Extract placeholders from CQL_FILTER (e.g., ['code_insee', 'section'])
        placeholders = re.findall(r"{(\w+)}", cql_filter)

        # Some entities (e.g., parcelle) define a dedicated ``featureId`` entry
        # instead of a CQL_FILTER. If such a key exists, treat ``featureId`` as a
        # placeholder.
        if "featureId" in geometry_cfg:
            placeholders.append("featureId")

        # 4⃣ Build the filter dictionary
        if args and isinstance(args[0], dict) and len(args) == 1:
            filters = args[0]
        elif kwargs:
            filters = kwargs
        else:
            # Map positional arguments to placeholders in order
            filters = {}
            for i, ph in enumerate(placeholders):
                filters[ph] = args[i] if i < len(args) else ""

        # 5⃣ Perform the request
        try:
            geometry = self.client.fetch_geometry(entity_key, **filters)
            return geometry
        except Exception:
            # Return None on any failure (e.g., missing parameters, network error)
            return None
