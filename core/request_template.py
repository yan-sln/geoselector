"""Request template abstraction for GeoSelector.

This module defines a minimal ``RequestTemplate`` protocol that the ``ApiClient``
depends on, and provides a concrete ``WfsRequestTemplate`` implementation for the
current WFS service. Additional APIs can be supported by adding new classes that
implement the same protocol.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


class RequestTemplate(Protocol):
    """Protocol defining the ``build`` method required by :class:`ApiClient`.

    Implementations must return a mapping of query parameters ready for
    ``urllib.parse.urlencode``.
    """

    def build(
        self,
        typename: str,
        propertyname: str,
        cql: str | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class WfsRequestTemplate:
    """Concrete request template for the existing WFS API.

    The fields correspond to the ``common`` section of ``config/apis.json``.
    """

    SERVICE: str = "WFS"
    VERSION: str = "2.0.0"
    REQUEST: str = "GetFeature"
    OUTPUTFORMAT: str = "application/json"

    def build(
        self,
        typename: str,
        propertyname: str,
        cql: str | None = None,
        **extra: Any,
    ) -> Mapping[str, Any]:
        params: dict[str, Any] = {
            "SERVICE": self.SERVICE,
            "VERSION": self.VERSION,
            "REQUEST": self.REQUEST,
            "OUTPUTFORMAT": self.OUTPUTFORMAT,
            "TYPENAME": typename,
            "PROPERTYNAME": propertyname,
        }
        if cql is not None:
            params["CQL_FILTER"] = cql
        params.update(extra)
        return params
