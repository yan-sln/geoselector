"""Configuration utilities for GeoSelector.

This module defines the :class:`RequestTemplate` dataclass, which holds the constant
parameters required for every WFS request (SERVICE, VERSION, REQUEST, OUTPUTFORMAT).
It also provides a ``build`` method to construct the full query dictionary for a
specific request.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class RequestTemplate:
    """Dataclass containing the constant parts of a WFS request.

    The values correspond to the ``common`` section of ``config/apis.json``.
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
    ) -> Dict[str, Any]:
        """Return a dictionary ready to be URL‑encoded.

        Parameters
        ----------
        typename:
            The ``TYPENAME`` value for the entity.
        propertyname:
            The ``PROPERTYNAME`` value for the operation.
        cql:
            The ``CQL_FILTER`` string after placeholder substitution. ``None``
            means the parameter is omitted.
        **extra:
            Additional key/value pairs that should be added to the request (e.g.
            ``DISTINCT`` or pagination parameters).
        """
        params: Dict[str, Any] = {
            "SERVICE": self.SERVICE,
            "VERSION": self.VERSION,
            "REQUEST": self.REQUEST,
            "OUTPUTFORMAT": self.OUTPUTFORMAT,
            "TYPENAME": typename,
            "PROPERTYNAME": propertyname,
        }
        if cql is not None:
            params["CQL_FILTER"] = cql
        # Merge any extra parameters supplied by the caller.
        params.update(extra)
        return params
