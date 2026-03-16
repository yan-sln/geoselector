"""
Module contenant les sélecteurs d'entités (EntitySelector) et la factory (SelectorFactory).
"""

from typing import Type, List, Dict, TypeVar, Generic
from .entities import GeoEntity
from .api_client import StrategyRegistry
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=GeoEntity)

class EntitySelector(Generic[T]):
    """Interface pour les sélecteurs d'entités."""
    def select(self, text: str) -> List[T]:
        """Recherche d'entités."""
        raise NotImplementedError()

    def get_geometry(self, code: str, **kwargs) -> Dict:
        """Récupération de la géométrie."""
        raise NotImplementedError()

    def get_details(self, code: str, **kwargs) -> Dict:
        """Récupération des détails."""
        raise NotImplementedError()

class EntitySelectorImpl(EntitySelector[T]):
    """Implémentation concrète du sélecteur d'entités."""

    def __init__(self, entity_class: Type[T], api_source: str):
        self.entity_class = entity_class
        self.client_class = StrategyRegistry.get_client_class(api_source)
        self.client = self.client_class()

    def select(self, text: str) -> List[T]:
        """Recherche d'entités."""
        endpoint = self.entity_class.API_ENDPOINT
        try:
            raw_results = self.client.search(endpoint, text, limit=50)
            return [self.entity_class.from_api(item) for item in raw_results]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def get_geometry(self, code: str, **kwargs) -> Dict:
        """Récupération de la géométrie."""
        endpoint = self.entity_class.API_ENDPOINT
        try:
            # Request geometry (default behavior)
            return self.client.fetch_geometry(endpoint, code, **kwargs)
        except Exception as e:
            logger.error(f"Geometry fetch error: {e}")
            return {}

    def get_details(self, code: str, **kwargs) -> Dict:
        """Récupération des détails."""
        endpoint = self.entity_class.API_ENDPOINT
        try:
            # Request only identification details (no geometry)
            return self.client.fetch_geometry(endpoint, code, geometry=False, **kwargs)
        except Exception as e:
            logger.error(f"Details fetch error: {e}")
            return {}

class SelectorFactory:
    """Factory pour créer des sélecteurs d'entités."""
    _cache: Dict[str, EntitySelector] = {}

    @classmethod
    def create_selector(cls, entity_class: Type[T], api_source: str) -> EntitySelector[T]:
        """Crée un sélecteur avec cache."""
        cache_key = f"{entity_class.__name__}_{api_source}"
        if cache_key not in cls._cache:
            cls._cache[cache_key] = EntitySelectorImpl(entity_class, api_source)
            logger.info(f"Created new selector for {entity_class.__name__}")
        else:
            logger.debug(f"Using cached selector for {entity_class.__name__}")
        return cls._cache[cache_key]

    @classmethod
    def reset(cls):
        """Réinitialise le cache."""
        cls._cache.clear()