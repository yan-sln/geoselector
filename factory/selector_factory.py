"""
Factory de création de selectors
"""
from typing import TypeVar, Type, Dict
from core.selector import EntitySelector, EntitySelectorImpl
from core.service import GeoService
from core.strategy import ApiStrategy
from core.strategy_registry import get_strategy_class

# Added import for GeoEntity and debug logging
from core.entities import GeoEntity
import logging
logger = logging.getLogger(__name__)
logger.debug("GeoEntity imported: %s", GeoEntity)

T = TypeVar("T", bound=GeoEntity)

class SelectorFactory:
    """
    Factory simplifiée pour créer les selectors
    """

    _services: Dict[str, GeoService] = {}

    @classmethod
    def _get_service(cls, api_source: str) -> GeoService:
        """Retrieve or create a cached GeoService for the given API source."""
        if api_source not in cls._services:
            strategy_cls = get_strategy_class(api_source)
            strategy = strategy_cls()
            cls._services[api_source] = GeoService(strategy)
        return cls._services[api_source]

    @classmethod
    def reset(cls) -> None:
        """Clear cached services (useful after reconfiguration)."""
        cls._services.clear()

    @classmethod
    def create_selector(
        cls,
        entity_class: Type[T],
        api_source: str
    ) -> EntitySelector[T]:
        # Retrieve or create a cached GeoService for the requested API source
        service = cls._get_service(api_source)
        return EntitySelectorImpl(entity_class, service)