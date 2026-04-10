# flake8: noqa
"""API client for GeoSelector.

This module provides :class:`ApiClient` which loads the JSON configuration from
``config/apis.json`` and offers methods to build request URLs, perform cached
GET requests and expose high‑level ``search`` and ``fetch_geometry`` helpers.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, cast
import socket

from urllib.error import HTTPError, URLError
from .request_builder import get_request_builder
from .exceptions import ApiError, TimeoutError

from ..logging_config import logger


# Les exceptions ApiError sont maintenant définies dans entities.py
# Cette importation est conservée pour compatibilité mais ne sera plus utilisée
# Les classes spécifiques seront importées depuis entities.py


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
    def _escape_sql_value(self, value: str) -> str:
        """Escape a string value for use in SQL/CQL queries.

        This prevents injection attacks and handles special characters like
        apostrophes by doubling them, which is the standard approach for SQL.
        """
        if not isinstance(value, str):
            return str(value)
        # Double apostrophes to escape them in SQL/CQL
        escaped = value.replace("'", "''")
        return escaped

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
            # Escape values before formatting to prevent SQL injection
            escaped_values = {
                k: str(v).replace("'", "''") if isinstance(v, str) else v
                for k, v in values.items()
            }
            cql = cql_template.format(**escaped_values)
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
    def _handle_http_error(self, http_err: HTTPError, url: str) -> ApiError:
        """Handle HTTPError and convert it to ApiError."""
        error_msg = f"HTTP error {http_err.code}: {http_err.reason} when fetching {url}"
        logger.error(error_msg)
        return ApiError(error_msg, url)

    def _handle_url_error(self, url_err: URLError, url: str) -> ApiError:
        """Handle URLError and convert it to ApiError."""
        error_msg = f"URL error: {url_err.reason} when fetching {url}"
        logger.error(error_msg)
        return ApiError(error_msg, url)

    def _cached_get(self, url: str) -> Dict[str, Any]:
        """Perform a GET request and return the parsed JSON response.

        This method handles HTTP requests and error conversion. Caching is handled
        at a higher level in the calling code.
        """
        logger.debug("Fetching URL: %s", url)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                raw = resp.read().decode()
                # The response is expected to be a JSON object mapping strings to values.
                data: Dict[str, Any] = json.loads(raw)
                logger.info("Successful GET request to %s", url)
                return data
        except socket.timeout:
            # Handle socket timeout specifically and convert to TimeoutError
            error_msg = f"Request timeout when fetching {url}"
            logger.error(error_msg)
            raise TimeoutError(error_msg, url)
        except TimeoutError as timeout_err:
            # Handle TimeoutError specifically (from urllib when connection times out)
            error_msg = f"Request timeout when fetching {url}"
            logger.error(error_msg)
            raise TimeoutError(error_msg, url)
        except HTTPError as http_err:
            raise self._handle_http_error(http_err, url)
        except URLError as url_err:
            raise self._handle_url_error(url_err, url)
        except json.JSONDecodeError as json_err:
            error_msg = f"JSON decode error: {json_err.msg} when fetching {url}"
            logger.error(error_msg)
            raise ApiError(error_msg, url) from json_err
        except Exception as exc:
            error_msg = f"Unexpected error fetching {url}: {exc}"
            logger.error(error_msg)
            raise ApiError(error_msg, url) from exc

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
