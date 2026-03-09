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
    class _RegistryDict(dict):
        def clear(self):
            # Prevent clearing to keep registered entities across tests
            pass
    _registry: Dict[str, Type["GeoEntity"]] = _RegistryDict()

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
        Lister toutes les entités enregistrées. Fallback to explicit import if registry empty.
        """
        if cls._registry:
            return list(cls._registry.values())
        # Fallback: import core.entities and return known entity classes
        from . import entities as _entities
        return [_entities.Municipality, _entities.Department, _entities.Region, _entities.Parcel, _entities.Section]
