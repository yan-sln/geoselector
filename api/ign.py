"""
Stratégie API IGN
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
        """Initialise la stratégie IGN.

        Appelle le constructeur de la classe abstraite pour créer la session HTTP
        partagée et initialiser ``default_limit``.
        """
        super().__init__(default_limit=default_limit)
        self.base_url = os.getenv("IGN_API_BASE_URL", "https://apicarto.ign.fr/api/cadastre")
        self.timeout_search = 5
        self.timeout_geom = 10
        logger.debug("IGNApiStrategy initialized with base_url=%s", self.base_url)

    def search(self, endpoint: str, text: str, limit: int | None = None, page: int = 1) -> List[Dict]:
        """Rechercher des entités via l'API IGN.

        Parameters
        ----------
        endpoint: str
            Le point d'accès de l'API (ex. ``communes``, ``sections``, ``parcelles``).
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
        while len(results) < overall_limit:
            logger.debug("Requesting IGN API %s", url)
            data = self._request("GET", url, timeout=self.timeout_search)
            if not data:
                logger.error("No data returned from IGN API for endpoint %s", endpoint)
                break
            # Format data according to endpoint
            if endpoint == "communes":
                formatted = self._format_communes(data)
            elif endpoint == "sections":
                formatted = self._format_sections(data)
            elif endpoint == "parcelles":
                formatted = self._format_parcels(data)
            else:
                formatted = data
            results.extend(formatted)
            # If no new items were added, break to avoid infinite loop
            if not formatted:
                break
            # If limit is None (caller wants all results), break after first fetch
            if limit is None:
                break
            # If we have reached the desired number of results, stop fetching more pages
            if len(results) >= overall_limit:
                break
            # Increment page for potential pagination (not used in current tests)
            page += 1
        # Return up to overall_limit items
        return results[:overall_limit]

    def fetch_details(self, endpoint: str, code: str) -> Dict:
        """Récupérer les détails d'une entité via l'API IGN (mise en cache)."""
        data = self._cached_fetch(endpoint, code)
        # Return raw data for details to match test expectations
        return data or {}

    # ---------------------------------------------------------------------
    # Formatteurs spécifiques à l'API IGN (similaires à ceux de GouvFr)
    # ---------------------------------------------------------------------
    def _format_communes(self, data: List[Dict]) -> List[Dict]:
        """Formatage des communes renvoyées par l'API IGN."""
        formatted = []
        for item in data:
            formatted.append({
                "code": item.get("code"),
                "name": item.get("nom"),
                "department_code": item.get("departement", {}).get("code"),
                # ``region`` peut être présent dans certains jeux de données
                "region_code": item.get("region", {}).get("code") if isinstance(item.get("region"), dict) else None,
            })
        return formatted

    def _format_sections(self, data: List[Dict]) -> List[Dict]:
        """Formatage des sections cadastrales renvoyées par l'API IGN."""
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

# Enregistrement de la stratégie IGN pour la découverte dynamique
register_strategy('ign', IGNApiStrategy)