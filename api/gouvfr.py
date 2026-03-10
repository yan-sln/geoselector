"""
  Strategy API Géo.fr (geo.api.gouv.fr) - English documentation
  """

import logging
from typing import List, Dict
from core.strategy import ApiStrategy
from core.strategy_registry import register_strategy

logger = logging.getLogger(__name__)


class GouvFrApiStrategy(ApiStrategy):
    """Strategy API Géo.fr"""

    def __init__(self, default_limit: int = 10):
        """Initialize the GouvFr strategy with a shared session.

        Calls the abstract class constructor to create the shared HTTP session
        and initialize ``default_limit``.
        """
        super().__init__(default_limit=default_limit)
        self.base_url = "https://geo.api.gouv.fr"
        self.timeout_search = 5
        self.timeout_geom = 10

    def search(self, endpoint: str, text: str, limit: int | None = None, page: int = 1) -> List[Dict]:
        """Search for entities via Géo.fr with configurable ``limit`` and pagination.

        The method now delegates the pagination loop to the base class helper
        :meth:`core.strategy.ApiStrategy._paged_fetch` and provides a formatter
        that maps the raw API response to the canonical structure used by the
        rest of the library.
        """
        def formatter(data: List[Dict]) -> List[Dict]:
            if endpoint == "communes":
                return self._format_communes(data)
            elif endpoint == "departements":
                return self._format_departements(data)
            elif endpoint == "regions":
                return self._format_regions(data)
            elif endpoint == "parcelles":
                return self._format_parcels(data)
            elif endpoint == "sections":
                return self._format_sections(data)
            else:
                return data

        # Use the generic pagination helper from ApiStrategy.
        return self._paged_fetch(endpoint, text, limit=limit, page=page, formatter=formatter)

    def fetch_geometry(self, endpoint: str, code: str) -> Dict:
        """Retrieve geometry via Géo.fr (cached)."""
        return self._cached_fetch(endpoint, code, suffix="/geometry")

    def fetch_details(self, endpoint: str, code: str) -> Dict:
        """Récupérer les détails via Géo.fr (mise en cache)."""
        return self._cached_fetch(endpoint, code)

    def _format_communes(self, data: List[Dict]) -> List[Dict]:
        """Formatage des communes"""
        formatted = []
        for item in data:
            formatted.append({
                "code": item["code"],
                "name": item["nom"],
                "department_code": item["departement"]["code"],
            })
        return formatted

    def _format_departements(self, data: List[Dict]) -> List[Dict]:
        """Formatage des départements"""
        formatted = []
        for item in data:
            formatted.append({
                "code": item["code"],
                "name": item["nom"],
                "region_code": item["region"]["code"],
            })
        return formatted

    def _format_parcels(self, data: List[Dict]) -> List[Dict]:
        """Format parcels returned by the GouvFr API.

        Handles ``identifiant`` as name and extracts ``commune`` code.
        """
        formatted: List[Dict] = []
        for item in data:
            formatted.append({
                "code": item.get("code") or item.get("id"),
                "name": item.get("identifiant") or item.get("nom"),
                "commune_code": item.get("commune", {}).get("code"),
                "section": item.get("section", ""),
            })
        return formatted

    def _format_sections(self, data: List[Dict]) -> List[Dict]:
        """Format sections returned by the GouvFr API.

        Extracts ``commune`` code and keeps the section name.
        """
        formatted: List[Dict] = []
        for item in data:
            formatted.append({
                "code": item.get("code") or item.get("id"),
                "name": item.get("nom"),
                "commune_code": item.get("commune", {}).get("code"),
            })
        return formatted

    def _format_regions(self, data: List[Dict]) -> List[Dict]:
        """Formatage des régions"""
        formatted = []
        for item in data:
            formatted.append({
                "code": item["code"],
                "name": item["nom"],
            })
        return formatted

# Register the GouvFr strategy for dynamic lookup
register_strategy('gouvfr', GouvFrApiStrategy)
