from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class GeoEntity:
    """Base class – never instantiated directly."""
    code: str
    name: str


@dataclass(frozen=True)
class Municipality(GeoEntity):
    department_code: str


@dataclass(frozen=True)
class Department(GeoEntity):
    region_code: str


@dataclass(frozen=True)
class Region(GeoEntity):
    pass          # aucune donnée supplémentaire

__all__ = [
    "GeoEntity",
    "Municipality",
    "Department",
    "Region",
]