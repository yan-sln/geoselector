from typing import Optional
from qgis.core import QgsVectorLayer, QgsFeature
from ..selectors.entity_selector import EntitySelector

class EntityFeatureSelector:
    def __init__(self, selector: EntitySelector):
        self._selector = selector
        self._layer: Optional[QgsVectorLayer] = None
        self._selected_feature: Optional[QgsFeature] = None

    def select_feature(self) -> QgsFeature:
        """Sélection interactive d'un feature INCOMPLET"""
        # Ici, votre logique de sélection interactive QGIS
        # Exemple simplifié
        if self._layer is None:
            self.load_layer()
        
        # Logique de sélection QGIS ici
        # ...
        return self._selected_feature or QgsFeature()

    def get_selected(self) -> QgsFeature:
        """Retourne le feature sélectionné"""
        return self._selected_feature or QgsFeature()

    def load_layer(self) -> QgsVectorLayer:
        """Charge le layer correspondant"""
        # Exemple de chargement (à adapter selon vos besoins)
        if self._layer is None:
            layer_name = f"{self._selector.get_entity_type()}s"
            self._layer = QgsVectorLayer("Polygon", layer_name, "memory")
        return self._layer

    def get_selector(self) -> EntitySelector:
        """Retourne le sélecteur associé"""
        return self._selector
