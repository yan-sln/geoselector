"""
 IGN API Strategy
 """
from typing import List, Dict
from core.strategy import ApiStrategy
from core.strategy_registry import register_strategy
import os
import logging

logger = logging.getLogger(__name__)

class IGNApiStrategy(ApiStrategy):
    """
    Strategy API IGN
    """

    def __init__(self, default_limit: int = 10):
        """Initialize the IGN strategy.

        Calls the abstract class constructor to create the shared HTTP session
        and initialize ``default_limit``.
        """
        super().__init__(default_limit=default_limit)
        self.base_url = os.getenv("IGN_API_BASE_URL", "https://apicarto.ign.fr/api/cadastre")
        self.timeout_search = 5
        self.timeout_geom = 10
        logger.debug("IGNApiStrategy initialized with base_url=%s", self.base_url)

    def search(self, endpoint: str, text: str, limit: int | None = None, page: int = 1) -> List[Dict]:
        """Search for entities via the IGN API.

        The implementation now delegates pagination to the base class helper
        :meth:`core.strategy.ApiStrategy._paged_fetch`.
        """
        def formatter(data: List[Dict]) -> List[Dict]:
            if endpoint == "communes":
                return self._format_communes(data)
            elif endpoint == "sections":
                return self._format_sections(data)
            elif endpoint == "parcelles":
                return self._format_parcels(data)
            else:
                return data

        return self._paged_fetch(endpoint, text, limit=limit, page=page, formatter=formatter)

    def fetch_details(self, endpoint: str, code: str) -> Dict:
        """Retrieve the details of an entity via the IGN API (cached)."""
        data = self._cached_fetch(endpoint, code)
        # Return raw data for details to match test expectations
        return data or {}

    # ---------------------------------------------------------------------
    # Specific formatters for the IGN API (similar to those of GouvFr)
    # ---------------------------------------------------------------------
    def _format_communes(self, data: List[Dict]) -> List[Dict]:
        """Formatting of communes returned by the IGN API."""
        formatted = []
        for item in data:
            formatted.append({
                "code": item.get("code"),
                "name": item.get("nom"),
                "department_code": item.get("departement", {}).get("code"),
                # ``region`` may be present in some datasets
                "region_code": item.get("region", {}).get("code") if isinstance(item.get("region"), dict) else None,
            })
        return formatted

    def _format_sections(self, data: List[Dict]) -> List[Dict]:
        """Formatting of cadastral sections returned by the IGN API."""
        formatted = []
        for item in data:
            formatted.append({
                "code": item.get("code") or item.get("id"),
                "name": item.get("nom"),
                "commune_code": item.get("commune", {}).get("code"),
            })
        return formatted

    def _format_parcels(self, data: List[Dict]) -> List[Dict]:
        """Formatage des parcelles renvoyées par l'API IGN."""
        formatted = []
        for item in data:
            formatted.append({
                "code": item.get("code") or item.get("id"),
                "name": item.get("identifiant") or item.get("name"),
                "commune_code": item.get("commune", {}).get("code"),
                "section": item.get("section", ""),
            })
        return formatted

# Register the IGN strategy for dynamic discovery
register_strategy('ign', IGNApiStrategy)