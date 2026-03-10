"""
Geographic entities
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
    Base class for all geographic entities
    """
    API_ENDPOINT: str = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.API_ENDPOINT:
            EntityRegistry._register(cls)

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'GeoEntity':
        """
        Creation from a dictionary
        """
        pass

# -------------------------------
# Specific entities
# -------------------------------

class Municipality(GeoEntity):
    """
    Municipality entity
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
    Department entity
    """
    API_ENDPOINT = "departements"

    def __init__(self, code: str, name: str, region_code: Optional[str] = None):
        super().__init__(code, name)
        self.region_code = region_code

    @classmethod
    def from_dict(cls, data: dict) -> 'Department':
        """Create a Department instance from a dictionary.
        Supports both 'name' and 'nom' keys for the department name, and extracts
        the region code from either a direct 'region_code' field or a nested
        'region' dictionary as returned by the IGN API.
        """
        # Validate required 'code' field
        if 'code' not in data or not isinstance(data['code'], str):
            raise ValueError("Missing or invalid required field 'code'.")
        # Resolve name from 'name' or 'nom'
        name = data.get('name') or data.get('nom')
        if not isinstance(name, str):
            raise ValueError("Missing or invalid required field 'name'.")
        # Extract region_code if present and ensure it's a string
        region_code = None
        if 'region_code' in data:
            if isinstance(data['region_code'], str):
                region_code = data['region_code']
            else:
                raise ValueError("Invalid type for 'region_code'; expected string.")
        elif 'region' in data and isinstance(data['region'], dict):
            rc = data['region'].get('code')
            if isinstance(rc, str):
                region_code = rc
        return cls(
            code=data['code'],
            name=name,
            region_code=region_code
        )

class Region(GeoEntity):
    """
    Region entity
    """
    API_ENDPOINT = "regions"

    def __init__(self, code: str, name: str):
        super().__init__(code, name)

    @classmethod
    def from_dict(cls, data: dict) -> 'Region':
        """Create a Region instance from a dictionary.
        Accepts both 'name' and 'nom' keys for the region name.
        """
        # Validate required 'code'
        if 'code' not in data or not isinstance(data['code'], str):
            raise ValueError("Missing or invalid required field 'code'.")
        # Resolve name from 'name' or 'nom'
        name = data.get('name') or data.get('nom')
        if not isinstance(name, str):
            raise ValueError("Missing or invalid required field 'name'.")
        return cls(
            code=data['code'],
            name=name
        )

class Parcel(GeoEntity):
    """
    Parcel entity
    """
    API_ENDPOINT = "parcelles"

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
    Section entity
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
