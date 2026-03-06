"""
Stratégies d'API
"""
from abc import ABC, abstractmethod
from typing import List, Dict

class ApiStrategy(ABC):
    """
    Interface Strategy pour les API
    """
    base_url: str
    timeout_search: int
    timeout_geom: int

    @abstractmethod
    def search(self, endpoint: str, text: str) -> List[Dict]:
        """
        Rechercher des entités
        """
        pass

    @abstractmethod
    def fetch_geometry(self, endpoint: str, code: str) -> Dict:
        """
        Récupérer la géométrie
        """
        pass

    @abstractmethod
    def fetch_details(self, endpoint: str, code: str) -> Dict:
        """
        Récupérer les détails
        """
        pass