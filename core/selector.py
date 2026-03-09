"""
Selectors typés génériques
"""
from typing import Type, List, Dict, Generic, TypeVar
from abc import ABC, abstractmethod
from .service import GeoService
from .entities import GeoEntity

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
        results = self.service.search_entities(self.entity_class, text, limit=None)
        # Cast to List[T] to satisfy type checker; from_dict returns a subclass of GeoEntity
        from typing import cast
        return cast(List[T], [self.entity_class.from_dict(item) for item in results])

    def get_geometry(self, code: str) -> Dict:
        """
        Récupérer la géométrie
        """
        return self.service.fetch_entity_geometry(self.entity_class, code)

    def get_details(self, code: str) -> Dict:
        """
        Récupérer les détails
        """
        return self.service.get_entity_details(self.entity_class, code)