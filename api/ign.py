"""
Stratégie API IGN
"""
from typing import List, Dict
from core.strategy import ApiStrategy
from core.strategy_registry import register_strategy

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
        self.base_url = "https://apicarto.ign.fr/api"
        self.timeout_search = 5
        self.timeout_geom = 10

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
        current_page = page
        while len(results) < overall_limit:
            per_page = min(self.default_limit, overall_limit - len(results))
            params = {
                "q": text,
                "limit": per_page,
                "page": current_page,
            }
            data = self._request("GET", url, params=params, timeout=self.timeout_search)
            if not data:
                break
            # Formatte les données selon le endpoint
            if endpoint == "communes":
                formatted = self._format_communes(data)
            elif endpoint == "sections":
                formatted = self._format_sections(data)
            elif endpoint == "parcelles":
                formatted = self._format_parcels(data)
            else:
                formatted = data
            results.extend(formatted)
            if len(data) < per_page:
                break
            current_page += 1
        return results

    def fetch_details(self, endpoint: str, code: str) -> Dict:
        """Récupérer les détails d'une entité via l'API IGN (mise en cache)."""
        data = self._cached_fetch(endpoint, code)
        # Formatte selon le endpoint pour garder la même forme que le reste de l'application
        if endpoint == "communes":
            formatted = self._format_communes([data])
        elif endpoint == "sections":
            formatted = self._format_sections([data])
        elif endpoint == "parcelles":
            formatted = self._format_parcels([data])
        else:
            formatted = [data]
        return formatted[0] if formatted else {}

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
                "code": item.get("id"),
                "name": item.get("nom"),
                "commune_code": item.get("commune", {}).get("code"),
            })
        return formatted

    def _format_parcels(self, data: List[Dict]) -> List[Dict]:
        """Formatage des parcelles renvoyées par l'API IGN."""
        formatted = []
        for item in data:
            formatted.append({
                "code": item.get("id"),
                "name": item.get("identifiant"),
                "commune_code": item.get("commune", {}).get("code"),
                "section": item.get("section", ""),
            })
        return formatted

# Enregistrement de la stratégie IGN pour la découverte dynamique
register_strategy('ign', IGNApiStrategy)