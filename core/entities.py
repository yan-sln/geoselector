"""
Entités géographiques
"""
from typing import Optional
from abc import ABC, abstractmethod
from .registry import EntityRegistry

def _ensure_fields(data: dict, required: list[str], optional: list[str] = []) -> None:
    """Validate that required keys exist and are strings, and optional keys if present are strings.
    Raises:
        ValueError: if a required key is missing or not a string, or an optional key is present but not a string.
    """
    for key in required:
        if key not in data or not isinstance(data[key], str):
            raise ValueError(f"Missing or invalid required field '{key}'.")
    for key in optional:
        if key in data and not isinstance(data[key], str):
            raise ValueError(f"Invalid optional field '{key}': expected a string.")

class GeoEntity(ABC):
    """
    Classe de base pour toutes les entités géographiques
    """
    API_ENDPOINT: str = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.API_ENDPOINT:
            EntityRegistry.register(cls)

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'GeoEntity':
        """
        Création depuis un dictionnaire
        """
        pass

# -------------------------------
# Entités spécifiques
# -------------------------------

class Municipality(GeoEntity):
    """
    Entité commune
    """
    API_ENDPOINT = "communes"

    def __init__(self, code: str, name: str, department_code: Optional[str] = None):
        super().__init__(code, name)
        self.department_code = department_code

    @classmethod
    def from_dict(cls, data: dict) -> 'Municipality':
        # department_code is optional; name is required
        _ensure_fields(data, required=['code', 'name'], optional=['department_code'])
        return cls(
            code=data['code'],
            name=data['name'],
            department_code=data.get('department_code')
        )

class Department(GeoEntity):
    """
    Entité département
    """
    API_ENDPOINT = "departements"

    def __init__(self, code: str, name: str, region_code: Optional[str] = None):
        super().__init__(code, name)
        self.region_code = region_code

    @classmethod
    def from_dict(cls, data: dict) -> 'Department':
        # region_code is optional
        _ensure_fields(data, required=['code', 'name'], optional=['region_code'])
        return cls(
            code=data['code'],
            name=data['name'],
            region_code=data.get('region_code')
        )

class Region(GeoEntity):
    """
    Entité région
    """
    API_ENDPOINT = "regions"

    def __init__(self, code: str, name: str):
        super().__init__(code, name)

    @classmethod
    def from_dict(cls, data: dict) -> 'Region':
        _ensure_fields(data, required=['code', 'name'])
        return cls(
            code=data['code'],
            name=data['name']
        )

class Parcel(GeoEntity):
    """
    Entité parcelle cadastrale
    """
    API_ENDPOINT = "parcels"

    def __init__(self, code: str, name: str, commune_code: Optional[str] = None, section: Optional[str] = None):
        super().__init__(code, name)
        self.commune_code = commune_code
        self.section = section

    @classmethod
    def from_dict(cls, data: dict) -> 'Parcel':
        # commune_code is required, section is optional; name is required
        _ensure_fields(data, required=['code', 'commune_code', 'name'], optional=['section'])
        return cls(
            code=data['code'],
            name=data['name'],
            commune_code=data['commune_code'],
            section=data.get('section')
        )

class Section(GeoEntity):
    """
    Entité section cadastrale
    """
    API_ENDPOINT = "sections"

    def __init__(self, code: str, name: str, commune_code: Optional[str] = None):
        super().__init__(code, name)
        self.commune_code = commune_code

    @classmethod
    def from_dict(cls, data: dict) -> 'Section':
        # commune_code is required; name is required
        _ensure_fields(data, required=['code', 'commune_code', 'name'])
        return cls(
            code=data['code'],
            name=data['name'],
            commune_code=data['commune_code']
        )
