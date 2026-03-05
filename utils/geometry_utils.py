from qgis.core import QgsGeometry

class GeometryUtils:
    @staticmethod
    def geometry_to_qgs_geometry(geometry_data: dict) -> QgsGeometry:
        """Convertit un dictionnaire GeoJSON en ``QgsGeometry``.

        Le dictionnaire doit suivre la spécification GeoJSON (clés ``type``
        et ``coordinates``).  La fonction utilise ``QgsJsonUtils`` pour
        convertir le GeoJSON en une liste de ``QgsFeature`` puis renvoie la
        géométrie du premier feature.  Si le format est incorrect ou que la
        conversion échoue, une ``QgsGeometry`` vide est retournée.
        """
        import json
        from qgis.core import QgsJsonUtils

        if not isinstance(geometry_data, dict) or "type" not in geometry_data:
            return QgsGeometry()

        geojson_str = json.dumps(geometry_data)
        features = QgsJsonUtils.stringToFeatureList(geojson_str)
        if features:
            return features[0].geometry()
        return QgsGeometry()