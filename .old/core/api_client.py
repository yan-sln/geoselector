"""
Module définissant les clients API (ApiClient) pour les différentes sources.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Any
import requests
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class ApiClient(ABC):
    """Classe abstraite pour les clients d'API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # Configure proxy from environment variables for testing only.
        # The proxy URL can be set via the HTTP_PROXY or HTTPS_PROXY environment variables.
        # This keeps proxy credentials out of source control.
        import os
        proxy_url = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
        if proxy_url:
            self.session.proxies.update({
                'http': proxy_url,
                'https': proxy_url,
            })

    @abstractmethod
    def search(self, endpoint: str, text: str, limit: int) -> List[Dict]:
        """Recherche des entités."""
        pass

    @abstractmethod
    def fetch_geometry(self, endpoint: str, code: str, **kwargs) -> Dict:
        """Récupère la géométrie d'une entité."""
        pass

    def build_url(self, endpoint: str, code: str, **params) -> str:
        """Construit une URL basique."""
        url = f"{self.base_url}/{endpoint}"
        if code:
            url += f"/{code}"
        return url

    def _request(self, method: str, url: str, **kwargs) -> Dict:
        """Effectue une requête HTTP avec gestion des erreurs."""
        try:
            logger.debug(f"Requesting {method} {url}")
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Success: {method} {url}")
            return result
        except Exception as e:
            logger.error(f"Error requesting {url}: {e}")
            raise

class GouvFrApiClient(ApiClient):
    """Client API pour geo.api.gouv.fr"""

    def __init__(self):
        super().__init__("https://geo.api.gouv.fr")

    def search(self, endpoint: str, text: str, limit: int) -> List[Dict]:
        """Recherche d'entités via l'API Gouv.fr"""
        # Pour les recherches spécifiques
        if endpoint in ["regions", "departements", "communes"]:
            url = f"{self.base_url}/{endpoint}"
            # Build parameters: include 'q' only if a search text is provided.
            params: Dict[str, Any] = {"limit": limit}
            if text:
                params["q"] = text
            # Si c'est une recherche par nom exact, on peut utiliser 'nom'
            if endpoint == "regions":
                params = {"limit": limit}
                if text:
                    params["nom"] = text
            elif endpoint == "departements":
                params = {"limit": limit}
                if text:
                    params["nom"] = text
            elif endpoint == "communes":
                params = {"limit": limit}
                if text:
                    params["nom"] = text
            # The API may return a dict with 'features' or a list directly.
            result = self._request('GET', url, params=params)
            if isinstance(result, dict) and 'features' in result:
                return result['features']
            # Ensure we always return a list.
            if isinstance(result, dict):
                # If dict contains 'features', already handled above.
                # Otherwise, wrap the dict in a list.
                return [result]
            return result
        else:
            # Cas général
            url = f"{self.base_url}/{endpoint}"
            params = {"q": text, "limit": limit}
            result = self._request('GET', url, params=params)
            if isinstance(result, dict):
                # Return the list of features if present, otherwise attempt to extract a list.
                if 'features' in result:
                    return result['features']
                # Fallback: if the dict itself represents a single entity, wrap it in a list.
                return [result]
            # Assume the result is already a list of entities.
            return result

    def fetch_geometry(self, endpoint: str, code: str, **kwargs) -> Dict:
        """Récupère la géométrie en utilisant les URLs appropriées pour chaque source."""
        # Géométrie pour les entités Gouv.fr
        if endpoint in ["regions", "departements", "communes"]:
            # Determine if geometry is requested (default True)
            request_geometry = kwargs.get('geometry', True)
            if request_geometry:
                # URL with geometry fields
                if endpoint == "regions":
                    url = f"{self.base_url}/regions/{code}?fields=geometry"
                elif endpoint == "departements":
                    url = f"{self.base_url}/departements/{code}?fields=geometry"
                else:  # communes
                    url = f"{self.base_url}/communes?code={code}&fields=geometry"
                result = self._request('GET', url)
                # Return geometry if present, handling various response formats
                if isinstance(result, dict):
                    if "geometry" in result:
                        return result["geometry"]
                    if "features" in result and isinstance(result["features"], list) and result["features"]:
                        first_feat = result["features"][0]
                        if isinstance(first_feat, dict) and "geometry" in first_feat:
                            return first_feat["geometry"]
                if isinstance(result, list) and result:
                    first = result[0]
                    if isinstance(first, dict) and "geometry" in first:
                        return first["geometry"]
                return result
            else:
                # URL without geometry to fetch only identification (nom, code)
                if endpoint == "regions":
                    url = f"{self.base_url}/regions/{code}"
                elif endpoint == "departements":
                    url = f"{self.base_url}/departements?code={code}"
                else:  # communes
                    url = f"{self.base_url}/communes?code={code}"
                return self._request('GET', url)
        # Géométrie pour les entités IGN (déjà gérée avec le flag geometry=true)
        else:
            # Cas par défaut – conserve le comportement existant
            url = f"{self.base_url}/{endpoint}/{code}"
            return self._request('GET', url)

class IgnApiClient(ApiClient):
    """Client API pour apicarto.ign.fr"""

    def __init__(self):
        super().__init__("https://apicarto.ign.fr/api/cadastre")
        # Désactiver le proxy pour les requêtes IGN afin d'éviter les erreurs de connexion.
        self.session.proxies.clear()

    def search(self, endpoint: str, text: str, limit: int) -> List[Dict]:
        """Recherche d'entités via l'API IGN"""
        if endpoint == "parcelles":
            url = f"{self.base_url}/parcelle"
            params = {"q": text, "limit": limit}
        elif endpoint == "sections":
            url = f"{self.base_url}/section"
            params = {"q": text, "limit": limit}
        elif endpoint == "communes":
            url = f"{self.base_url}/commune"
            params = {"q": text, "limit": limit}
        else:
            url = f"{self.base_url}/{endpoint}"
            params = {"q": text, "limit": limit}

        try:
            result = self._request('GET', url, params=params)
            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Search error for {endpoint}: {e}")
            return []

    def fetch_geometry(self, endpoint: str, code: str, **kwargs) -> Dict:
        """Récupère la géométrie avec gestion des paramètres spécifiques."""
        departement = kwargs.get('departement', '') or kwargs.get('departement_code', '')
        # Construction des URLs spécifiques
        # Handle both singular and plural forms for parcel endpoint
        # Parcelle endpoint returns geometry by default; no extra geometry flag needed
        if endpoint in ("parcelle", "parcelles"):
            # Parcel endpoint returns full geometry without extra flag
            url = f"{self.base_url}/parcelle?codeParcelle={code}"
            if departement:
                url += f"&departement={departement}"
            # Use a longer timeout for parcel geometry request
            try:
                resp = self.session.get(url, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                # If the response is a FeatureCollection, return the first feature (or its geometry)
                if isinstance(data, dict) and "features" in data and isinstance(data["features"], list) and data["features"]:
                    # Return the first feature directly
                    return data["features"][0]
                # Otherwise return the raw data
                return data
            except Exception as e:
                logger.error(f"Error fetching parcel geometry: {e}")
                raise
        elif endpoint == "feuille":
            url = f"{self.base_url}/feuille?codeFeuille={code}"
            if departement:
                url += f"&departement={departement}"
            url += "&geometry=true"
        elif endpoint == "division":
            url = f"{self.base_url}/division?codeDivision={code}"
            if departement:
                url += f"&departement={departement}"
            url += "&geometry=true"
        elif endpoint == "commune":
            url = f"{self.base_url}/commune?codeInsee={code}"
            if departement:
                url += f"&departement={departement}"
            url += "&geometry=true"
        else:
            # Cas par défaut
            url = f"{self.base_url}/{endpoint}/{code}?geometry=true"
        return self._request('GET', url)

class StrategyRegistry:
    """Registre des classes de clients API."""
    _registry: Dict[str, type] = {}

    @classmethod
    def register_strategy(cls, name: str, client_class: type):
        """Enregistre une classe de client API."""
        cls._registry[name] = client_class
        logger.info(f"Registered API strategy: {name}")

    @classmethod
    def get_client_class(cls, name: str) -> type | None:
        """Retourne la classe de client API correspondante, ou None si non enregistrée."""
        return cls._registry.get(name)

# Enregistrement des stratégies
StrategyRegistry.register_strategy("gouvfr", GouvFrApiClient)
StrategyRegistry.register_strategy("ign", IgnApiClient)