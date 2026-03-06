"""
Factory de création de selectors
"""
from typing import TypeVar, Type
from ..core.selector import EntitySelector, EntitySelectorImpl
from ..core.service import GeoService
from ..core.strategy import ApiStrategy
from ..api.ign import IGNApiStrategy
from ..api.gouvfr import GouvFrApiStrategy

# Added import for GeoEntity and debug logging
from ..core.entities import GeoEntity
import logging
logger = logging.getLogger(__name__)
logger.debug("GeoEntity imported: %s", GeoEntity)

T = TypeVar("T", bound=GeoEntity)

class SelectorFactory:
    """
    Factory simplifiée pour créer les selectors
    """

    STRATEGIES = {
        "IGN": IGNApiStrategy,
        "GOUVFR": GouvFrApiStrategy
    }

    @classmethod
    def create_selector(
        cls,
        entity_class: Type[T],
        api_source: str
    ) -> EntitySelector[T]:
        strategy_class = cls.STRATEGIES[api_source]
        strategy = strategy_class()
        service = GeoService(strategy)
        return EntitySelectorImpl(entity_class, service)