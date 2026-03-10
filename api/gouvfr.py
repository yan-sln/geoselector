"""
Stratégie API Géo.fr (geo.api.gouv.fr)
"""

import logging
from typing import List, Dict
from core.strategy import ApiStrategy
from core.strategy_registry import register_strategy
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class GouvFrApiStrategy(ApiStrategy):
    """Strategy API Géo.fr"""

    def __init__(self, default_limit: int = 10):
        """Initialise la stratégie GouvFr avec session partagée.

        Appelle le constructeur de la classe abstraite pour créer la session HTTP
        partagée et initialiser ``default_limit``.
        """
        super().__init__(default_limit=default_limit)
        self.base_url = "https://geo.api.gouv.fr"
        self.timeout_search = 5
        self.timeout_geom = 10

    def search(self, endpoint: str, text: str, limit: int | None = None, page: int = 1) -> List[Dict]:
        """Rechercher des entités via Géo.fr avec support du ``limit`` configurable et de la pagination.

        Parameters
        ----------
        endpoint: str
            Le point d'accès de l'API (ex. ``communes``).
        text: str
            Le texte de recherche.
        limit: int | None, optional
            Nombre maximal de résultats souhaités. Si ``None``, utilise ``default_limit``.
        page: int, optional
            Page de résultats à récupérer (début à 1).
        """
        url = f"{self.base_url}/{endpoint}"
        overall_limit = self.get_limit(limit)
        results: List[Dict] = []
        current_page = page
        while len(results) < overall_limit:
            per_page = min(self.default_limit, overall_limit - len(results))
            params = {
                "q": quote_plus(text),
                "limit": per_page,
                "page": current_page,
            }
            logger.debug("Requesting GouvFr API %s with params %s", url, params)
            data = self._request("GET", url, params=params, timeout=self.timeout_search)
            if not data:
                logger.error("No data returned from GouvFr API for endpoint %s", endpoint)
                break
            # Formatte les données selon le endpoint
            if endpoint == "communes":
                formatted = self._format_communes(data)
            elif endpoint == "departements":
                formatted = self._format_departements(data)
            elif endpoint == "regions":
                formatted = self._format_regions(data)
            else:
                formatted = data
            results.extend(formatted)
            logger.info("GouvFr %s returned %d items (page %d)", endpoint, len(formatted), current_page)
            if len(data) < per_page:
                break
            current_page += 1
        return results

    def fetch_geometry(self, endpoint: str, code: str) -> Dict:
        """Récupérer la géométrie via Géo.fr (mise en cache)."""
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
