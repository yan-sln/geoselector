"""
Selectors typés génériques
"""

import logging
from typing import Type, List, Dict, Generic, TypeVar
from abc import ABC, abstractmethod
from .service import GeoService
from .entities import GeoEntity

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=GeoEntity)

class EntitySelector(Generic[T], ABC):
    """
    Interface du selector typé
    """
    entity_class: Type[T]

    @abstractmethod
    def select(self, text: str) -> List[T]:
        """
        Rechercher des entités
        """
        pass

    @abstractmethod
    def get_geometry(self, code: str) -> Dict:
        """
        Récupérer la géométrie
        """
        pass

    @abstractmethod
    def get_details(self, code: str) -> Dict:
        """
        Récupérer les détails
        """
        pass

class EntitySelectorImpl(EntitySelector[T]):
    """
    Selector générique typé
    """

    def __init__(self, entity_class: Type[T], service: GeoService):
        self.entity_class = entity_class
        self.service = service

    def select(self, text: str) -> List[T]:
        """
        Rechercher des entités
        """
        logger.debug("Selecting entities for %s with text='%s'", self.entity_class.__name__, text)
        results = self.service.search_entities(self.entity_class, text, limit=None)
        logger.info("Selector returned %d results for %s", len(results), self.entity_class.__name__)
        # Cast to List[T] to satisfy type checker; from_dict returns a subclass of GeoEntity
        from typing import cast
        return cast(List[T], [self.entity_class.from_dict(item) for item in results])

    def get_geometry(self, code: str) -> Dict:
        """
        Récupérer la géométrie
        """
        logger.debug("Fetching geometry for %s code=%s", self.entity_class.__name__, code)
        geometry = self.service.fetch_entity_geometry(self.entity_class, code)
        logger.info("Fetched geometry for %s code=%s", self.entity_class.__name__, code)
        return geometry

    def get_details(self, code: str) -> Dict:
        """
        Récupérer les détails
        """
        logger.debug("Fetching details for %s code=%s", self.entity_class.__name__, code)
        details = self.service.get_entity_details(self.entity_class, code)
        logger.info("Fetched details for %s code=%s", self.entity_class.__name__, code)
        return details
