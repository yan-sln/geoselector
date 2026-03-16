"""
Module contenant les entités géographiques (GeoEntity)
et le registre d'entités (EntityRegistry).
"""

from typing import Type, Dict, List, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class EntityRegistry:
    """Registre centralisé des classes d'entités géographiques."""
    _registry: Dict[str, Type['GeoEntity']] = {}

    @classmethod
    def register(cls, entity_class: Type['GeoEntity']):
        """Enregistre une classe d'entité si elle a un API_ENDPOINT."""
        if hasattr(entity_class, 'API_ENDPOINT') and entity_class.API_ENDPOINT:
            cls._registry[entity_class.API_ENDPOINT] = entity_class
            logger.info(f"Registered entity: {entity_class.__name__}")

    @classmethod
    def get(cls, endpoint: str) -> Type['GeoEntity']:
        """Retourne la classe d'entité associée à un endpoint."""
        return cls._registry.get(endpoint)

class GeoEntity(ABC):
    """Classe abstraite représentant une entité géographique."""
    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name

    @classmethod
    @abstractmethod
    def from_api(cls, raw: dict) -> 'GeoEntity':
        """Crée une instance à partir d'une donnée brute."""
        pass

# Méta-classe pour l'enregistrement automatique
class GeoEntityMeta(type):
    """Méta-classe pour l'enregistrement automatique des GeoEntity."""
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if 'API_ENDPOINT' in attrs and attrs['API_ENDPOINT']:
            EntityRegistry.register(new_class)
        return new_class

# Entités Gouv.fr
class Region(GeoEntity):
    API_ENDPOINT = "regions"
    SOURCE_ID = "gouvfr"

    @classmethod
    def from_api(cls, raw: dict) -> 'Region':
        return cls(
            code=raw["code"],
            name=raw["nom"]
        )

class Department(GeoEntity):
    API_ENDPOINT = "departements"
    SOURCE_ID = "gouvfr"

    def __init__(self, code: str, name: str, region_code: Optional[str] = None):
        super().__init__(code, name)
        self.region_code = region_code

    @classmethod
    def from_api(cls, raw: dict) -> 'Department':
        return cls(
            code=raw["code"],
            name=raw["nom"],
            region_code=raw.get("region", {}).get("code")
        )

class Municipality(GeoEntity):
    API_ENDPOINT = "communes"
    SOURCE_ID = "gouvfr"

    def __init__(self, code: str, name: str, department_code: Optional[str] = None):
        super().__init__(code, name)
        self.department_code = department_code

    @classmethod
    def from_api(cls, raw: dict) -> 'Municipality':
        return cls(
            code=raw["code"],
            name=raw["nom"],
            department_code=raw.get("departement", {}).get("code")
        )

# Entités IGN
class Parcel(GeoEntity):
    API_ENDPOINT = "parcelles"
    SOURCE_ID = "ign"

    def __init__(self, code: str, name: str, commune_code: Optional[str] = None, section: Optional[str] = None):
        super().__init__(code, name)
        self.commune_code = commune_code
        self.section = section

    @classmethod
    def from_api(cls, raw: dict) -> 'Parcel':
        return cls(
            code=raw["code"],
            name=raw["nom"],
            commune_code=raw.get("commune_code"),
            section=raw.get("section")
        )

class Section(GeoEntity):
    API_ENDPOINT = "sections"
    SOURCE_ID = "ign"

    def __init__(self, code: str, name: str, commune_code: Optional[str] = None):
        super().__init__(code, name)
        self.commune_code = commune_code

    @classmethod
    def from_api(cls, raw: dict) -> 'Section':
        return cls(
            code=raw["code"],
            name=raw["nom"],
            commune_code=raw.get("commune_code")
        )