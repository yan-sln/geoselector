import json
import urllib.parse
import urllib.request
from typing import List, Dict, Union
from qgis.core import QgsGeometry, QgsJsonUtils
from .geo_entity import Municipality, Department, Region, GeoEntity

class GeoDataService:
    API_BASE_URL = "https://geo.api.gouv.fr"

    def search_entities(self, entity_type: str, text: str) -> List[GeoEntity]:
        """Recherche d'entités par type et texte"""
        if len(text) < 2:
            return []
            
        # Mapping des types d'entités vers leurs endpoints
        endpoints = {
            "municipality": "communes",
            "department": "departements", 
            "region": "regions"
        }
        
        if entity_type not in endpoints:
            raise ValueError(f"Type d'entité non supporté: {entity_type}")
            
        endpoint = endpoints[entity_type]
        fields = self._get_fields_for_entity_type(entity_type)
        
        params = urllib.parse.urlencode({
            "nom": text,
            "fields": fields,
            "limit": "5"
        })
        url = f"{self.API_BASE_URL}/{endpoint}?{params}"
        
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                return self._parse_entities(entity_type, data)
        except Exception:
            return []

    def fetch_entity_geometry(self, entity_type: str, code: str) -> QgsGeometry | None:
        """Récupération de la géométrie d'une entité"""
        # Mapping des types d'entités vers leurs endpoints
        endpoints = {
            "municipality": "communes",
            "department": "departements", 
            "region": "regions"
        }
        
        if entity_type not in endpoints:
            raise ValueError(f"Type d'entité non supporté: {entity_type}")
            
        endpoint = endpoints[entity_type]
        params = urllib.parse.urlencode({"geometry": "contour", "format": "geojson"})
        url = f"{self.API_BASE_URL}/{endpoint}/{code}?{params}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                feature_collection = json.dumps({
                    "type": "FeatureCollection",
                    "features": [{
                        "type": "Feature",
                        "geometry": data["geometry"],
                        "properties": {},
                    }],
                })
                features = QgsJsonUtils.stringToFeatureList(feature_collection)
                if features:
                    return features[0].geometry()
                return None
        except Exception:
            return None

    def _get_fields_for_entity_type(self, entity_type: str) -> str:
        """Retourne les champs appropriés pour chaque type d'entité"""
        fields_map = {
            "municipality": "nom,code,codeDepartement",
            "department": "nom,code,codeRegion",
            "region": "nom,code"
        }
        return fields_map.get(entity_type, "nom,code")

    def _parse_entities(self, entity_type: str, data: List[Dict]) -> List[GeoEntity]:
        """Parse les résultats API selon le type d'entité"""
        if entity_type == "municipality":
            return [
                Municipality(code=c["code"], name=c["nom"], departmentCode=c["codeDepartement"])
                for c in data
            ]
        elif entity_type == "department":
            return [
                Department(code=c["code"], name=c["nom"], regionCode=c["codeRegion"])
                for c in data
            ]
        else:  # region
            return [
                Region(code=c["code"], name=c["nom"])
                for c in data
            ]