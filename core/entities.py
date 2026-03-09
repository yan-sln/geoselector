"""
Entités géographiques
"""
from typing import Optional
from abc import ABC, abstractmethod
from .registry import EntityRegistry

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
        code = data.get('code')
        name = data.get('name')
        if not code or not name:
            raise ValueError("Code and name are required")
        return cls(
            code=code,
            name=name,
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
        code = data.get('code')
        name = data.get('name')
        if not code or not name:
            raise ValueError("Code and name are required")
        return cls(
            code=code,
            name=name,
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
        code = data.get('code')
        name = data.get('name')
        if not code or not name:
            raise ValueError("Code and name are required")
        return cls(
            code=code,
            name=name
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
        code = data.get('code')
        name = data.get('name')
        if not code or not name:
            raise ValueError("Code and name are required")
        return cls(
            code=code,
            name=name,
            commune_code=data.get('commune_code'),
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
        code = data.get('code')
        name = data.get('name')
        if not code or not name:
            raise ValueError("Code and name are required")
        return cls(
            code=code,
            name=name,
            commune_code=data.get('commune_code')
        )