# "Entity definitions for GeoSelector.

"""Entity definitions for GeoSelector.

This module defines an abstract base class :class:`GeoEntity` and concrete
sub‑classes for each geographical entity described in ``config/apis.json``.
Each subclass provides a ``from_api`` classmethod to build an instance from the
raw feature dictionary returned by the WFS service.
"""

# flake8: noqa
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar

# Import the new exception for validation
from .exceptions import InvalidParameterFormat

# Forward declaration for type hinting.
Self = TypeVar("Self", bound="GeoEntity")


class GeoEntity(abc.ABC):
    """Base class for all geographical entities.

    Sub‑classes must define a ``code`` attribute (or a suitable identifier) and
    implement :meth:`from_api`. The ``_geometry`` attribute is populated lazily
    via :meth:`get_geometry`.
    """

    _geometry: Optional[Dict[str, Any]] = None
    _service: Optional["GeoService"] = None  # type: ignore

    # ------------------------
    # Identity (must be stable)
    # ------------------------

    @property
    @abc.abstractmethod
    def code(self) -> str:
        """Unique immutable identifier."""
        raise NotImplementedError

    # ------------------------
    # Equality & hashing
    # ------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GeoEntity):
            return NotImplemented
        return self.code == other.code and type(self) is type(other)

    def __hash__(self) -> int:
        """Return hash of the entity based on its code."""
        return hash((type(self), self.code))

    # ------------------------
    # Mutable state (controlled)
    # ------------------------

    def set_service(self, service: "GeoService") -> None:  # type: ignore
        """Inject the :class:`GeoService` used to fetch additional data."""
        object.__setattr__(self, "_service", service)

    def _set_geometry(self, geometry: Dict[str, Any]) -> None:
        object.__setattr__(self, "_geometry", geometry)

    def get_geometry(self, force: bool = False) -> Optional[Dict[str, Any]]:
        """Return the geometry dictionary.

        If ``force`` is ``True`` the geometry is fetched anew, overwriting any
        cached value. If ``force`` is ``False`` and the geometry is not yet cached,
        it is fetched and stored for future calls.
        """
        if self._service is None:
            return self._geometry

        if force or self._geometry is None:
            geometry = self._service.fetch_entity_geometry(type(self), self)
            self._set_geometry(geometry)

        return self._geometry

    def has_geometry(self) -> bool:
        """Return ``True`` if geometry is already cached."""
        return self._geometry is not None

    # ------------------------
    # Factory
    # ------------------------

    @classmethod
    @abc.abstractmethod
    def from_api(cls: Type[Self], raw: Dict[str, Any]) -> Self:
        """Create an instance from a raw feature dictionary returned by the API."""
        raise NotImplementedError
    
    @classmethod
    def _validate_and_create_entity(
        cls: Type[Self],
        raw: Dict[str, Any],
        required_fields: list[str],
        field_mapping: dict[str, str],
    ) -> Self:
        """Validate required fields and create entity instance."""
        props = raw.get("properties", {})

        # Validate required fields
        for field in required_fields:
            if field not in props or not props.get(field):
                raise InvalidParameterFormat(
                    field,
                    "non-empty string",
                    str(props.get(field)) if props.get(field) is not None else "None",
                )

        # Map fields to constructor args
        kwargs = {
            prop_name: props.get(field_name)
            for prop_name, field_name in field_mapping.items()
        }

        if "code" in kwargs:
            kwargs["_code"] = kwargs.pop("code")

        return cls(**kwargs)


# Concrete entity definitions -------------------------------------------------


@dataclass(frozen=True, eq=False)
class Region(GeoEntity):
    """Geographic region entity."""

    _code: str
    name: Optional[str] = None

    @property
    def code(self) -> str:
        return self._code

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Region":
        return cls._validate_and_create_entity(
            raw,
            required_fields=["code_insee"],
            field_mapping={"code": "code_insee", "name": "nom_officiel"},
        )


@dataclass(frozen=True, eq=False)
class Departement(GeoEntity):
    """Geographic department entity."""

    _code: str
    name: Optional[str] = None

    @property
    def code(self) -> str:
        return self._code

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Departement":
        return cls._validate_and_create_entity(
            raw,
            required_fields=["code_insee"],
            field_mapping={"code": "code_insee", "name": "nom_officiel"},
        )


@dataclass(frozen=True, eq=False)
class Commune(GeoEntity):
    """Geographic commune entity."""

    _code: str
    name: Optional[str] = None

    @property
    def code(self) -> str:
        return self._code

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Commune":
        return cls._validate_and_create_entity(
            raw,
            required_fields=["code_insee"],
            field_mapping={"code": "code_insee", "name": "nom_com"},
        )


@dataclass(frozen=True, eq=False)
class Arrondissement(GeoEntity):
    """Geographic arrondissement entity."""

    code_insee: str
    name: Optional[str] = None
    code_arr: Optional[str] = None

    @property
    def code(self) -> str:  # type: ignore[override]
        return f"{self.code_insee}_{self.code_arr}"

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Arrondissement":
        return cls._validate_and_create_entity(
            raw,
            required_fields=["code_insee", "code_arr"],
            field_mapping={
                "code_insee": "code_insee",
                "name": "nom_arr",
                "code_arr": "code_arr",
            },
        )


@dataclass(frozen=True, eq=False)
class Section(GeoEntity):
    """Geographic section entity."""

    code_insee: str
    section: Optional[str] = None

    @property
    def code(self) -> str:  # type: ignore[override]
        return f"{self.code_insee}_{self.section}"

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Section":
        return cls._validate_and_create_entity(
            raw,
            required_fields=["code_insee", "section"],
            field_mapping={"code_insee": "code_insee", "section": "section"},
        )


@dataclass(frozen=True, eq=False)
class Feuille(GeoEntity):
    """Geographic feuille entity."""

    code_insee: str
    section: Optional[str] = None
    feuille: Optional[str] = None

    @property
    def code(self) -> str:  # type: ignore[override]
        return f"{self.code_insee}_{self.section}_{self.feuille}"

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Feuille":
        return cls._validate_and_create_entity(
            raw,
            required_fields=["code_insee", "section", "feuille"],
            field_mapping={
                "code_insee": "code_insee",
                "section": "section",
                "feuille": "feuille",
            },
        )


@dataclass(frozen=True, eq=False)
class Parcelle(GeoEntity):
    """Geographic parcel entity."""

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
        # For Parcelle, we use raw['id'] for feature_id (as requested)
        feature_id = raw.get("id")

        # Validate that feature_id was extracted properly
        if not feature_id:
            raise InvalidParameterFormat(
                "feature_id",
                "non-empty string",
                str(feature_id) if feature_id is not None else "None",
            )

        # Direct instantiation - simple and clean
        props = raw.get("properties", {})
        return cls(
            feature_id=feature_id,
            code_insee=props.get("code_insee"),
            section=props.get("section"),
            numero=props.get("numero"),
            idu=props.get("idu"),
        )


@dataclass(frozen=True, eq=False)
class SubdivisionFiscale(GeoEntity):
    """Geographic subdivision fiscale entity."""

    gid: str
    idu_parcel: Optional[str] = None
    lettre: Optional[str] = None

    @property
    def code(self) -> str:  # type: ignore[override]
        return self.gid

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "SubdivisionFiscale":
        return cls._validate_and_create_entity(
            raw,
            required_fields=["gid"],
            field_mapping={
                "gid": "gid",
                "idu_parcel": "idu_parcel",
                "lettre": "lettre",
            },
        )
