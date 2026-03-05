from typing import Optional
from qgis.core import QgsGeometry
from ..core.geo_service import GeoDataService
from ..core.geo_entity import GeoEntity

class EntitySelector:
    def __init__(self, service: GeoDataService, entity_type: str):
        self._service = service
        self._entity_type = entity_type
        self._selected_item: Optional[GeoEntity] = None

    def select(self, text: str) -> GeoEntity:
        """Sélection d'une entité par texte"""
        entities = self._service.search_entities(self._entity_type, text)
        if not entities:
            raise ValueError(f"Aucune entité trouvée pour le type {self._entity_type}")
        
        selected = entities[0]  # Simplifié pour exemple
        self._selected_item = selected
        return selected

    def get_selected_item(self) -> GeoEntity:
        """Retourne l'entité sélectionnée"""
        if self._selected_item is None:
            raise ValueError("Aucune entité sélectionnée")
        return self._selected_item

    def load_geometry(self, code: str) -> QgsGeometry | None:
        """Charge la géométrie d'une entité"""
        return self._service.fetch_entity_geometry(self._entity_type, code)

    def get_entity_type(self) -> str:
        """Retourne le type d'entité"""
        return self._entity_type