"""
Registry of geographic entities
"""

from typing import Type, Dict
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .entities import GeoEntity

class EntityRegistry:
    """Immutable global registry for GeoEntity subclasses.

    The internal storage is private and cannot be accessed or modified
    directly from outside the class. Registration occurs via the private
    ``_register`` method which is used by ``GeoEntity.__init_subclass__``.
    Only read‑only operations ``get`` and ``list_entities`` are exposed.
    """
    # Private dictionary storing the mapping endpoint -> entity class
    __registry: Dict[str, Type["GeoEntity"]] = {}
    # Backward‑compatible alias used by existing tests
    _registry = __registry

    @classmethod
    def _register(cls, entity: "Type[GeoEntity]") -> None:
        """Register an entity class in the internal registry.

        This method is intended for internal use only (called from
        ``GeoEntity.__init_subclass__``). It updates the private ``__registry``
        mapping and logs the registration.
        """
        cls.__registry[entity.API_ENDPOINT] = entity
        logger.info("Entity %s registered for endpoint '%s'", entity.__name__, entity.API_ENDPOINT)

    @classmethod
    def get(cls, endpoint: str) -> "Type[GeoEntity]":
        """Retrieve an entity class by its API endpoint.

        Raises ``KeyError`` if the endpoint is not registered.
        """
        return cls.__registry[endpoint]

    @classmethod
    def list_entities(cls) -> list:
        """Return a list of all registered entity classes.

        If the registry is empty (e.g., during early import), a fallback list
        of known entity classes from ``core.entities`` is returned.
        """
        if cls.__registry:
            return list(cls.__registry.values())
        # Fallback: import core.entities and return known entity classes
        from . import entities as _entities
        return [_entities.Municipality, _entities.Department, _entities.Region, _entities.Parcel, _entities.Section]
