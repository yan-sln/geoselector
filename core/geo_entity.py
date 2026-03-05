from typing import TypedDict

class GeoEntity(TypedDict):
    code: str
    name: str

class Municipality(GeoEntity):
    departmentCode: str

class Department(GeoEntity):
    regionCode: str

class Region(GeoEntity):
    pass  # Aucun champ supplémentaire requis pour les régions
