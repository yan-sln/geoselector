"""
Service central pour interroger les API
"""
from typing import TypeVar, Type, List, Dict
from .strategy import ApiStrategy
from .entities import GeoEntity

T = TypeVar("T", bound=GeoEntity)

class GeoService:
    """
    Service central pour interroger les API
    """

    def __init__(self, strategy: ApiStrategy):
        self.strategy = strategy

    def search_entities(self, entity_class: Type[T], text: str, limit: int | None = None) -> List[Dict]:
        endpoint = entity_class.API_ENDPOINT
        return self.strategy.search(endpoint, text, limit)

    def fetch_entity_geometry(self, entity_class: Type[T], code: str) -> Dict:
        endpoint = entity_class.API_ENDPOINT
        return self.strategy.fetch_geometry(endpoint, code)

    def get_entity_details(self, entity_class: Type[T], code: str) -> Dict:
        endpoint = entity_class.API_ENDPOINT
        return self.strategy.fetch_details(endpoint, code)