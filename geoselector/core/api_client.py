# flake8: noqa
"""API client for GeoSelector.

This module provides :class:`ApiClient` which loads the JSON configuration from
``config/apis.json`` and offers methods to build request URLs, perform cached
GET requests and expose high‑level ``search`` and ``fetch_geometry`` helpers.
"""

from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from .request_builder import get_request_builder

from ..logging_config import logger


class ApiError(RuntimeError):
    """Custom exception for API‑related errors."""

    def __init__(self, message: str, url: str | None = None):
        """Initialize the ApiError with an error message and optional URL.

        Parameters
        ----------
        message: str
            Human‑readable error description.
        url: str | None, optional
            The request URL that caused the error, if applicable.
        """
        super().__init__(message)
        self.url = url


class ApiClient:
    """Client that knows how to talk to the WFS service defined in ``apis.json``.

    Parameters
    ----------
    config_path:
        Path to the JSON configuration file. Defaults to ``config/apis.json``
        relative to the project root.
    """

    def __init__(self, config_path: str | Path | None = None):
        # Resolve default config file packaged with the library
        if config_path is None:
            # Path to the directory containing this file, then up to package root
            base_dir = Path(__file__).resolve().parent.parent
            config_path = base_dir / "config" / "apis.json"
        self.config_path = Path(config_path)
        if not self.config_path.is_file():
            raise FileNotFoundError(f"API configuration not found: {self.config_path}")
        with self.config_path.open(encoding="utf-8") as f:
            self.config: Dict[str, Any] = json.load(f)
        logger.debug("Loaded API configuration from %s", self.config_path)

        # Load configuration and obtain a request builder function.
        # The builder abstracts the creation of request parameters for the
        # specific API type (currently only WFS is implemented).
        self.builder = get_request_builder(self.config)

        # Base URL for all requests.
        self.base_url: str = self.config.get("base_url", "")
        if not self.base_url:
            raise ValueError("'base_url' missing in API configuration")

    # ---------------------------------------------------------------------
    # URL construction helpers
    # ---------------------------------------------------------------------
    def _build_url(self, entity: str, operation: str, **values: Any) -> str:
        """Construct a full request URL for *entity* and *operation*.

        ``entity`` corresponds to a key in the ``entities`` section of the JSON
        configuration (e.g. ``"region"``). ``operation`` is the name of the block
        inside that entity (e.g. ``"search_by_name"``).
        ``values`` are the placeholder substitutions required by the operation's
        ``CQL_FILTER``.
        """
        entities_cfg = self.config.get("entities", {})
        if entity not in entities_cfg:
            raise KeyError(f"Entity '{entity}' not defined in configuration")
        entity_cfg = entities_cfg[entity]
        if operation not in entity_cfg:
            raise KeyError(f"Operation '{operation}' not defined for entity '{entity}'")
        op_cfg = entity_cfg[operation]

        typename = entity_cfg.get("TYPENAME")
        propertyname = op_cfg.get("PROPERTYNAME")
        cql_template = op_cfg.get("CQL_FILTER")
        # Some operations (e.g. geometry) may have a ``featureId`` key.
        feature_id = op_cfg.get("featureId")

        # Replace placeholders in the CQL filter.
        cql: Optional[str] = None
        if isinstance(cql_template, str):
            cql = cql_template.format(**values)
        elif cql_template is None:
            cql = None
        else:
            raise TypeError("CQL_FILTER must be a string or null")

        # Extra parameters such as DISTINCT, COUNT, etc. are taken from the
        # operation block if present and not already supplied via ``values``.
        extra: Dict[str, Any] = {}
        for key, val in op_cfg.items():
            if key in {"PROPERTYNAME", "CQL_FILTER", "featureId"}:
                continue
            # If the caller already supplied a value for this key, keep the
            # caller's value.
            if key in values:
                extra[key] = values[key]
            else:
                extra[key] = val

        if "limit" in values:
            # Prefer the caller‑supplied limit and store it under the WFS‑expected name
            extra["COUNT"] = values["limit"]

        # Build the full parameter dictionary using the request builder.
        # Ensure the resulting mapping is mutable.
        params = dict(
            self.builder(
                typename=typename,
                propertyname=propertyname,
                cql=cql,
                **extra,
            )
        )

        # Some operations require a ``featureId`` placeholder to be added to the
        # URL path rather than the query string. For simplicity we treat it as a
        # regular query parameter when present.
        if feature_id:
            params["featureId"] = feature_id.format(**values)

        query = urllib.parse.urlencode(params)
        url = f"{self.base_url}?{query}"
        logger.debug("Built URL for %s/%s: %s", entity, operation, url)
        return url

    # ---------------------------------------------------------------------
    # HTTP helpers
    # ---------------------------------------------------------------------
    @lru_cache(maxsize=256)
    def _cached_get(self, url: str) -> Dict[str, Any]:
        """Perform a GET request and return the parsed JSON response.

        The result is cached using ``functools.lru_cache`` to avoid repeated
        network calls for identical URLs.
        """
        logger.debug("Fetching URL: %s", url)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                raw = resp.read().decode()
                # The response is expected to be a JSON object mapping strings to values.
                data: Dict[str, Any] = json.loads(raw)
                logger.info("Successful GET request to %s", url)
                return data
        except Exception as exc:
            logger.error("Error fetching %s: %s", url, exc)
            raise ApiError(str(exc), url) from exc

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def search(self, entity: str, mode: str, **values: Any) -> List[Dict[str, Any]]:
        """Search for *entity* using *mode* (e.g. ``"search_by_name"``).

        Returns the list of feature dictionaries from the ``features`` key of the
        response. If the response does not contain ``features`` an empty list is
        returned.
        """
        url = self._build_url(entity, mode, **values)
        data = self._cached_get(url)
        return cast(List[Dict[str, Any]], data.get("features", []))

    def fetch_geometry(self, entity: str, **values: Any) -> Optional[Dict[str, Any]]:
        """Fetch geometry for *entity*.

        Returns the geometry dictionary of the first feature, or ``None`` if no
        feature is found.
        """
        url = self._build_url(entity, "geometry", **values)
        data = self._cached_get(url)
        features = data.get("features", [])
        if not features:
            return None
        # Geometry may be stored under ``geometry`` or as a property named
        # ``geom``. We return the raw geometry object.
        first = features[0]
        geometry = first.get("geometry")
        if geometry is None:
            # Fallback to a property called ``geom``.
            geometry = first.get("properties", {}).get("geom")
        return cast(Optional[Dict[str, Any]], geometry)
