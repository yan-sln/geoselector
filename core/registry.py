"""
Registry des entités géographiques
"""

from __future__ import annotations
from typing import Type, Dict
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .entities import GeoEntity

class EntityRegistry:
    """
    Registry global des entités
    """
    _registry: Dict[str, Type["GeoEntity"]] = {}

    @classmethod
    def register(cls, entity: "Type[GeoEntity]") -> None:
        """
        Enregistrer une entité
        """
        cls._registry[entity.API_ENDPOINT] = entity
        logger.info("Entity %s registered for endpoint '%s'", entity.__name__, entity.API_ENDPOINT)

    @classmethod
    def get(cls, endpoint: str) -> "Type[GeoEntity]":
        """
        Récupérer une entité par endpoint
        """
        return cls._registry[endpoint]

    @classmethod
    def list_entities(cls) -> list:
        """
        Lister toutes les entités enregistrées
        """
        return list(cls._registry.values())
