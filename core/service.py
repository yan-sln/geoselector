"""
 Central service for querying the APIs
 """

import logging
from typing import TypeVar, Type, List, Dict
from .strategy import ApiStrategy
from .entities import GeoEntity

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=GeoEntity)

class GeoService:
    """Central service for querying the various geographic APIs.

    The service delegates the actual HTTP work to an ``ApiStrategy``
    implementation (e.g. :class:`api.gouvfr.GouvFrApiStrategy` or
    :class:`api.ign.IGNApiStrategy`). It provides thin, typed wrappers around
    the strategy methods and adds logging for tracing.
    """

    def __init__(self, strategy: ApiStrategy):
        """Create a ``GeoService`` with the given ``strategy``.

        Parameters
        ----------
        strategy: ApiStrategy
            Concrete strategy instance responsible for the HTTP requests.
        """
        self.strategy = strategy

    def search_entities(self, entity_class: Type[T], text: str, limit: int | None = None) -> List[Dict]:
        """Search for entities of ``entity_class`` matching ``text``.

        Parameters
        ----------
        entity_class: Type[T]
            The concrete :class:`core.entities.GeoEntity` subclass to search.
        text: str
            Search query string.
        limit: int | None, optional
            Maximum number of results to return. ``None`` uses the strategy's
            default limit.
        """
        endpoint = entity_class.API_ENDPOINT
        logger.debug("Searching entities for endpoint %s with text='%s' limit=%s", endpoint, text, limit)
        results = self.strategy.search(endpoint, text, limit)
        logger.info("Search returned %d results for endpoint %s", len(results), endpoint)
        return results

    def fetch_entity_geometry(self, entity_class: Type[T], code: str) -> Dict:
        """Fetch geometry for a specific entity identified by ``code``.

        Parameters
        ----------
        entity_class: Type[T]
            The entity type whose geometry is requested.
        code: str
            Unique identifier of the entity.
        """
        endpoint = entity_class.API_ENDPOINT
        logger.debug("Fetching geometry for endpoint %s code=%s", endpoint, code)
        geometry = self.strategy.fetch_geometry(endpoint, code)
        logger.info("Fetched geometry for endpoint %s code=%s", endpoint, code)
        return geometry

    def get_entity_details(self, entity_class: Type[T], code: str) -> Dict:
        """Retrieve detailed information for a specific entity.

        Parameters
        ----------
        entity_class: Type[T]
            The entity type.
        code: str
            Unique identifier of the entity.
        """
        endpoint = entity_class.API_ENDPOINT
        logger.debug("Fetching details for endpoint %s code=%s", endpoint, code)
        details = self.strategy.fetch_details(endpoint, code)
        logger.info("Fetched details for endpoint %s code=%s", endpoint, code)
        return details
