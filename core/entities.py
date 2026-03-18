"""Entity definitions for GeoSelector.

This module defines an abstract base class :class:`GeoEntity` and concrete
sub‑classes for each geographical entity described in ``config/apis.json``.
Each subclass provides a ``from_api`` classmethod to build an instance from the
raw feature dictionary returned by the WFS service.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type, TypeVar

# Forward declaration for type hinting.
Self = TypeVar("Self", bound="GeoEntity")


class GeoEntity(abc.ABC):
    """Base class for all geographical entities.

    Sub‑classes must define a ``code`` attribute (or a suitable identifier) and
    implement :meth:`from_api`. The ``_geometry`` attribute is populated lazily
    via :meth:`get_geometry`.
    """

    code: str
    _geometry: Optional[Dict[str, Any]] = None
    _service: Optional["GeoService"] = None  # type: ignore  # forward reference

    def set_service(self, service: "GeoService") -> None:  # type: ignore
        """Inject the :class:`GeoService` used to fetch additional data."""
        self._service = service

    def get_geometry(self, force: bool = False) -> Optional[Dict[str, Any]]:
        """Return the geometry dictionary.

        If ``force`` is ``True`` the geometry is fetched anew, overwriting any
        cached value. If ``force`` is ``False`` and the geometry is not yet cached,
        it is fetched and stored for future calls.
        """
        if self._service is None:
            return self._geometry
        if force or self._geometry is None:
            self._geometry = self._service.fetch_entity_geometry(type(self), self.code)
        return self._geometry

    def has_geometry(self) -> bool:
        """Return ``True`` if geometry is already cached."""
        return self._geometry is not None

    @classmethod
    @abc.abstractmethod
    def from_api(cls: Type[Self], raw: Dict[str, Any]) -> Self:
        """Create an instance from a raw feature dictionary returned by the API."""
        raise NotImplementedError


# Concrete entity definitions -------------------------------------------------


@dataclass
class Region(GeoEntity):
    code: str
    name: Optional[str] = None

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Region":
        props = raw.get("properties", {})
        return cls(code=props.get("code_insee"), name=props.get("nom_officiel"))


@dataclass
class Departement(GeoEntity):
    code: str
    name: Optional[str] = None

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Departement":
        props = raw.get("properties", {})
        return cls(code=props.get("code_insee"), name=props.get("nom_officiel"))


@dataclass
class Commune(GeoEntity):
    code: str
    name: Optional[str] = None

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Commune":
        props = raw.get("properties", {})
        return cls(code=props.get("code_insee"), name=props.get("nom_com"))


@dataclass
class Arrondissement(GeoEntity):
    code_insee: str
    name: Optional[str] = None
    code_arr: Optional[str] = None

    @property
    def code(self) -> str:  # type: ignore[override]
        return f"{self.code_insee}_{self.code_arr}"

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Arrondissement":
        props = raw.get("properties", {})
        return cls(
            code_insee=props.get("code_insee"),
            name=props.get("nom_arr"),
            code_arr=props.get("code_arr"),
        )

@dataclass
class Section(GeoEntity):
    code_insee: str
    section: Optional[str] = None

    @property
    def code(self) -> str:  # type: ignore[override]
        return f"{self.code_insee}_{self.section}"

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Section":
        props = raw.get("properties", {})
        return cls(
            code_insee=props.get("code_insee"),
            section=props.get("section"),
        )

@dataclass
class Feuille(GeoEntity):
    code_insee: str
    section: Optional[str] = None
    feuille: Optional[str] = None

    @property
    def code(self) -> str:  # type: ignore[override]
        return f"{self.code_insee}_{self.section}_{self.feuille}"

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Feuille":
        props = raw.get("properties", {})
        return cls(
            code_insee=props.get("code_insee"),
            section=props.get("section"),
            feuille=props.get("feuille"),
        )

@dataclass
class Parcelle(GeoEntity):
    feature_id: str
    code_insee: Optional[str] = None
    section: Optional[str] = None
    numero: Optional[str] = None
    idu: Optional[str] = None

    @property
    def code(self) -> str:  # type: ignore[override]
        return self.feature_id

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Parcelle":
        props = raw.get("properties", {})
        return cls(
            feature_id=raw.get("id") or props.get("feature_id"),
            code_insee=props.get("code_insee"),
            section=props.get("section"),
            numero=props.get("numero"),
            idu=props.get("idu"),
        )


@dataclass
class SubdivisionFiscale(GeoEntity):
    gid: str
    idu_parcel: Optional[str] = None
    lettre: Optional[str] = None

    @property
    def code(self) -> str:  # type: ignore[override]
        return self.gid

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "SubdivisionFiscale":
        props = raw.get("properties", {})
        return cls(
            gid=props.get("gid"),
            idu_parcel=props.get("idu_parcel"),
            lettre=props.get("lettre"),
        )
