"""Lightweight request builder factory for GeoSelector.

The goal is to decouple the construction of request parameters from the
``ApiClient`` while keeping the implementation simple.  The module provides:

* ``load_api_config`` – reads ``config/apis.json``.
* ``wfs_builder`` – builds a parameter dictionary for the existing WFS API.
* ``rest_builder`` – placeholder for a future REST‑style API (example).
* ``get_request_builder`` – selects the appropriate builder based on the
  ``api_type`` field in the configuration (defaults to ``"wfs"``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Mapping, Any


def load_api_config(path: str = "config/apis.json") -> dict:
    """Load the JSON configuration file.

    Returns the parsed dictionary.  Raises ``FileNotFoundError`` if the file
    does not exist.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"API configuration not found: {config_path}")
    with config_path.open(encoding="utf-8") as f:
        return json.load(f)


def wfs_builder(common: dict) -> Callable[..., Mapping[str, Any]]:
    """Return a builder function for the WFS API.

    The returned ``build`` function matches the signature used by the original
    ``RequestTemplate`` dataclass.
    """
    def build(
        typename: str,
        propertyname: str,
        cql: str | None = None,
        **extra: Any,
    ) -> Mapping[str, Any]:
        params: dict[str, Any] = {
            "SERVICE": common.get("SERVICE", "WFS"),
            "VERSION": common.get("VERSION", "2.0.0"),
            "REQUEST": common.get("REQUEST", "GetFeature"),
            "OUTPUTFORMAT": common.get("OUTPUTFORMAT", "application/json"),
            "TYPENAME": typename,
            "PROPERTYNAME": propertyname,
        }
        if cql is not None:
            params["CQL_FILTER"] = cql
        params.update(extra)
        return params

    return build


def rest_builder(common: dict) -> Callable[..., Mapping[str, Any]]:
    """Placeholder for a future REST API builder.

    This example simply returns the ``extra`` mapping unchanged; real
    implementations would translate the arguments into the appropriate query
    parameters or request body.
    """
    def build(endpoint: str, **extra: Any) -> Mapping[str, Any]:
        # Example: include a base endpoint and any extra query parameters.
        params: dict[str, Any] = {"endpoint": endpoint}
        params.update(extra)
        return params

    return build


def get_request_builder(config: dict) -> Callable:
    """Select the appropriate request builder based on ``api_type``.

    ``api_type`` defaults to ``"wfs"`` for backward compatibility.
    """
    api_type = config.get("api_type", "wfs")
    common = config.get("common", {})
    if api_type == "wfs":
        return wfs_builder(common)
    if api_type == "rest":
        return rest_builder(common)
    raise ValueError(f"Unsupported api_type: {api_type}")
