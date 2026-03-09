"""
Service central pour interroger les API
"""

import logging
from typing import TypeVar, Type, List, Dict
from .strategy import ApiStrategy
from .entities import GeoEntity

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=GeoEntity)

class GeoService:
    """
    Service central pour interroger les API
    """

    def __init__(self, strategy: ApiStrategy):
        self.strategy = strategy

    def search_entities(self, entity_class: Type[T], text: str, limit: int | None = None) -> List[Dict]:
        endpoint = entity_class.API_ENDPOINT
        logger.debug("Searching entities for endpoint %s with text='%s' limit=%s", endpoint, text, limit)
        results = self.strategy.search(endpoint, text, limit)
        logger.info("Search returned %d results for endpoint %s", len(results), endpoint)
        return results

    def fetch_entity_geometry(self, entity_class: Type[T], code: str) -> Dict:
        endpoint = entity_class.API_ENDPOINT
        logger.debug("Fetching geometry for endpoint %s code=%s", endpoint, code)
        geometry = self.strategy.fetch_geometry(endpoint, code)
        logger.info("Fetched geometry for endpoint %s code=%s", endpoint, code)
        return geometry

    def get_entity_details(self, entity_class: Type[T], code: str) -> Dict:
        endpoint = entity_class.API_ENDPOINT
        logger.debug("Fetching details for endpoint %s code=%s", endpoint, code)
        details = self.strategy.fetch_details(endpoint, code)
        logger.info("Fetched details for endpoint %s code=%s", endpoint, code)
        return details
