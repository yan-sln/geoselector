"""
Stratégie API Géo.fr (geo.api.gouv.fr)
"""
import requests
from typing import List, Dict
from ..core.strategy import ApiStrategy

class GouvFrApiStrategy(ApiStrategy):
    """
    Strategy API Géo.fr
    """

    def __init__(self):
        self.base_url = "https://geo.api.gouv.fr"
        self.timeout_search = 5
        self.timeout_geom = 10

    def search(self, endpoint: str, text: str) -> List[Dict]:
        """
        Rechercher des entités via Géo.fr
        """
        url = f"{self.base_url}/{endpoint}"

        params = {
            'q': text,
            'limit': 10
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout_search)
            response.raise_for_status()

            data = response.json()
            # Formatage spécifique selon l'endpoint
            if endpoint == 'communes':
                return self._format_communes(data)
            elif endpoint == 'departements':
                return self._format_departements(data)
            elif endpoint == 'regions':
                return self._format_regions(data)
            elif endpoint == 'parcels':
                return self._format_parcels(data)
            elif endpoint == 'sections':
                return self._format_sections(data)
            else:
                return data

        except requests.RequestException as e:
            print(f"Erreur Géo.fr recherche {endpoint}: {e}")
            return []

    def fetch_geometry(self, endpoint: str, code: str) -> Dict:
        """
        Récupérer la géométrie via Géo.fr
        """
        url = f"{self.base_url}/{endpoint}/{code}/geometry"

        try:
            response = requests.get(url, timeout=self.timeout_geom)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Erreur Géo.fr géométrie {endpoint}/{code}: {e}")
            return {}

    def fetch_details(self, endpoint: str, code: str) -> Dict:
        """
        Récupérer les détails via Géo.fr
        """
        url = f"{self.base_url}/{endpoint}/{code}"

        try:
            response = requests.get(url, timeout=self.timeout_geom)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Erreur Géo.fr détails {endpoint}/{code}: {e}")
            return {}

    def _format_communes(self, data: List[Dict]) -> List[Dict]:
        """
        Formatage des communes
        """
        formatted = []
        for item in data:
            formatted.append({
                'code': item['code'],
                'name': item['nom'],
                'department_code': item['departement']['code']
            })
        return formatted

    def _format_departements(self, data: List[Dict]) -> List[Dict]:
        """
        Formatage des départements
        """
        formatted = []
        for item in data:
            formatted.append({
                'code': item['code'],
                'name': item['nom'],
                'region_code': item['region']['code']
            })
        return formatted

    def _format_regions(self, data: List[Dict]) -> List[Dict]:
        """
        Formatage des régions
        """
        formatted = []
        for item in data:
            formatted.append({
                'code': item['code'],
                'name': item['nom']
            })
        return formatted

    def _format_parcels(self, data: List[Dict]) -> List[Dict]:
        """
        Formatage des parcelles
        """
        formatted = []
        for item in data:
            formatted.append({
                'code': item['id'],
                'name': item['identifiant'],
                'commune_code': item['commune']['code'],
                'section': item.get('section', '')
            })
        return formatted

    def _format_sections(self, data: List[Dict]) -> List[Dict]:
        """
        Formatage des sections
        """
        formatted = []
        for item in data:
            formatted.append({
                'code': item['id'],
                'name': item['nom'],
                'commune_code': item['commune']['code']
            })
        return formatted