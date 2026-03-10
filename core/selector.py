"""
 Generic typed selectors
 """

import logging
from typing import Type, List, Dict, Generic, TypeVar
from abc import ABC, abstractmethod
from .service import GeoService
from .entities import GeoEntity

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=GeoEntity)

class EntitySelector(Generic[T], ABC):
    """Abstract, typed selector interface.

    Concrete implementations retrieve entities of a specific ``GeoEntity``
    subclass from an underlying API strategy. The three abstract methods
    provide a minimal contract used throughout the library.
    """
    entity_class: Type[T]

    @abstractmethod
    def select(self, text: str) -> List[T]:
        """Search for entities matching ``text``.

        Parameters
        ----------
        text: str
            Search query.

        Returns
        -------
        List[T]
            List of entity instances matching the query.
        """
        pass

    @abstractmethod
    def get_geometry(self, code: str) -> Dict:
        """Retrieve geometry for the entity identified by ``code``.

        Parameters
        ----------
        code: str
            Unique identifier of the entity.

        Returns
        -------
        dict
            Geometry data as returned by the API.
        """
        pass

    @abstractmethod
    def get_details(self, code: str) -> Dict:
        """Retrieve detailed information for the entity identified by ``code``.

        Parameters
        ----------
        code: str
            Unique identifier of the entity.

        Returns
        -------
        dict
            Detailed entity data.
        """
        pass

class EntitySelectorImpl(EntitySelector[T]):
    """
     Generic typed selector
     """

    def __init__(self, entity_class: Type[T], service: GeoService):
        self.entity_class = entity_class
        self.service = service

    def select(self, text: str) -> List[T]:
        """
        Search for entities
        """
        logger.debug("Selecting entities for %s with text='%s'", self.entity_class.__name__, text)
        results = self.service.search_entities(self.entity_class, text, limit=None)
        # Removed duplicate info log (service already logs result count)
        from typing import cast
        return cast(List[T], [self.entity_class.from_dict(item) for item in results])

    def get_geometry(self, code: str) -> Dict:
        """
        Retrieve geometry
        """
        logger.debug("Fetching geometry for %s code=%s", self.entity_class.__name__, code)
        geometry = self.service.fetch_entity_geometry(self.entity_class, code)
        logger.info("Fetched geometry for %s code=%s", self.entity_class.__name__, code)
        return geometry

    def get_details(self, code: str) -> Dict:
        """
        Retrieve details
        """
        logger.debug("Fetching details for %s code=%s", self.entity_class.__name__, code)
        details = self.service.get_entity_details(self.entity_class, code)
        logger.info("Fetched details for %s code=%s", self.entity_class.__name__, code)
        return details
