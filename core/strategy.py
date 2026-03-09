"""
 Stratégies d'API
 """
from abc import ABC, abstractmethod
from typing import List, Dict
import requests
import logging

logger = logging.getLogger(__name__)
from functools import lru_cache

class ApiStrategy(ABC):
    """
    Interface Strategy pour les API
    """
    base_url: str
    timeout_search: int
    timeout_geom: int

    def __init__(self, default_limit: int = 10) -> None:
        """Initialise les attributs communs.

        - ``self.session`` : session HTTP partagée pour réutiliser les connexions.
        - ``self.default_limit`` : valeur par défaut du paramètre ``limit`` utilisé dans ``search``.
        """
        self.session = requests.Session()
        self.base_url = ""
        self.timeout_search = 5
        self.timeout_geom = 10
        self.default_limit = default_limit

    def _request(self, method: str, url: str, **kwargs):
        """Wrapper générique autour de ``requests``.

        Gère les erreurs, applique le timeout de recherche et renvoie le JSON décodé.
        """
        logger.debug("Request %s %s kwargs=%s", method, url, kwargs)
        try:
            response = self.session.request(method, url, timeout=self.timeout_search, **kwargs)
            response.raise_for_status()
            data = response.json()
            logger.info("Successful %s request to %s – received %s", method, url, type(data).__name__)
            return data
        except requests.RequestException as e:
            logger.error(f"[ApiStrategy] {method} {url} → {e}")
            return None

    @abstractmethod
    def search(self, endpoint: str, text: str, limit: int | None = None) -> List[Dict]:
        """Rechercher des entités"""
        ...

    def fetch_geometry(self, endpoint: str, code: str) -> Dict:
        """Récupérer la géométrie (mise en cache)."""
        # Utilise le suffixe '/geometry' pour les géométries
        return self._cached_fetch(endpoint, code, suffix="/geometry")

    def fetch_details(self, endpoint: str, code: str) -> Dict:
        """Récupérer les détails (mise en cache)."""
        return self._cached_fetch(endpoint, code)

    @lru_cache(maxsize=256)
    def _cached_fetch(self, endpoint: str, code: str, suffix: str = "") -> Dict:
        """Récupère et met en cache le résultat d'une requête GET.

        ``suffix`` permet d'ajouter un segment d'URL (ex. ``/geometry``).
        """
        url = f"{self.base_url}/{endpoint}/{code}{suffix}"
        data = self._request("GET", url, timeout=self.timeout_geom)
        return data or {}

    def get_limit(self, limit: int | None) -> int:
        """Retourne la valeur du paramètre ``limit`` en utilisant la valeur fournie ou la valeur par défaut."""
        return limit if limit is not None else self.default_limit

    def reset_session(self) -> None:
        """Ferme la session HTTP actuelle et en crée une nouvelle.

        Utile lorsqu’on veut réinitialiser les connexions ou appliquer de nouvelles
        configurations (ex. proxy, headers) sans recréer l’objet stratégie.
        """
        self.session.close()
        self.session = requests.Session()

    def clear_cache(self) -> None:
        """Vide le cache LRU utilisé par ``_cached_fetch``.

        Cela force les prochains appels à refaire les requêtes HTTP.
        """
        self._cached_fetch.cache_clear()

