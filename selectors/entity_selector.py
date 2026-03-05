from __future__ import annotations
from typing import Optional
from qgis.core import QgsGeometry

from ..core.geo_service import GeoDataService
from ..core.entities import GeoEntity
from ..core.exceptions import EntityNotFoundError, InvalidEntityTypeError

class EntitySelector:
    """Sélecteur générique d’entités (municipalité, département, région)."""

    def __init__(self, service: GeoDataService, entity_type: str):
        self._service = service
        self._entity_type = entity_type
        self._selected_item: Optional[GeoEntity] = None

    # -----------------------------------------------------------------
    def select(self, text: str) -> GeoEntity:
        """Recherche l’entité la plus pertinente à partir d’un texte."""
        try:
            entity = self._service.search_entities(self._entity_type, text)[0]
        except (EntityNotFoundError, InvalidEntityTypeError) as exc:
            # On laisse le logger du service faire le job, on re‑raise pour
            # que le caller puisse gérer le problème.
            raise exc

        self._selected_item = entity
        return entity

    # -----------------------------------------------------------------
    def get_selected_item(self) -> GeoEntity:
        if self._selected_item is None:
            raise ValueError("Aucune entité sélectionnée")
        return self._selected_item

    # -----------------------------------------------------------------
    def load_geometry(self, code: str) -> QgsGeometry | None:
        """Récupère la géométrie via le service."""
        return self._service.fetch_entity_geometry(self._entity_type, code)

    # -----------------------------------------------------------------
    def get_entity_type(self) -> str:
        return self._entity_type