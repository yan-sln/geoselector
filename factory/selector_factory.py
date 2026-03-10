"""
 Factory for creating selectors
 """
from typing import TypeVar, Type, Dict, TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # Imported only for type checking to avoid circular imports at runtime
    from core.entities import GeoEntity
    from core.selector import EntitySelector, EntitySelectorImpl
    from core.service import GeoService
    from core.strategy_registry import get_strategy_class

T = TypeVar("T", bound="GeoEntity")

class SelectorFactory:
    """
    Factory for creating selectors
    """

    _services: Dict[str, "GeoService"] = {}

    @classmethod
    def _get_service(cls, api_source: str) -> "GeoService":
        """Retrieve or create a cached GeoService for the given API source."""
        # Local imports to avoid circular dependencies at runtime
        from core.service import GeoService
        from core.strategy_registry import get_strategy_class

        if api_source in cls._services:
            logger.debug("Cache hit for API source '%s'", api_source)
            return cls._services[api_source]
        logger.debug("Cache miss for API source '%s' – creating new service", api_source)
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
    ) -> "EntitySelector[T]":
        """Create a selector for the given entity class and API source."""
        # Local import to avoid circular dependency
        from core.selector import EntitySelectorImpl
        service = cls._get_service(api_source)
        logger.info("Creating selector for %s using API source '%s'", entity_class.__name__, api_source)
        return EntitySelectorImpl(entity_class, service)
