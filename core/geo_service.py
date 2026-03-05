from __future__ import annotations
import json
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any

import yaml
from qgis.core import QgsGeometry, QgsJsonUtils

from .entities import Municipality, Department, Region, GeoEntity
from .exceptions import (
    InvalidEntityTypeError,
    GeoApiError,
    EntityNotFoundError,
)
from ..logging_config import configure_logging
from .. import CONFIG_PATH  # défini dans geoselector/__init__.py (voir plus bas)

# -------------------------------------------------------------------------
#   Chargement de la configuration (singleton)
# -------------------------------------------------------------------------
_cfg_raw = yaml.safe_load(Path(CONFIG_PATH).read_text(encoding="utf-8"))
CONFIG = _cfg_raw["api"]
ENDPOINTS = _cfg_raw["endpoints"]
FIELDS = _cfg_raw["fields"]

logger = configure_logging(_cfg_raw)

# -------------------------------------------------------------------------
class GeoDataService:
    """Service d’accès à l’API geo.api.gouv.fr."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or CONFIG["base_url"]
        self.timeout_search = CONFIG["timeout"]["search"]
        self.timeout_geom   = CONFIG["timeout"]["geometry"]

    # -----------------------------------------------------------------
    def _build_url(self, endpoint: str, params: dict[str, str]) -> str:
        query = urllib.parse.urlencode(params)
        return f"{self.base_url}/{endpoint}?{query}"

    # -----------------------------------------------------------------
    def _http_get(self, url: str, timeout: int) -> Any:
        """Effectue la requête GET et renvoie le JSON décodé.
        Lève GeoApiError en cas de problème réseau ou HTTP."""
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                payload = resp.read().decode()
                logger.debug("GET %s → %s bytes", url, len(payload))
                return json.loads(payload)
        except urllib.error.HTTPError as e:
            logger.error("HTTP %s %s – %s", e.code, e.reason, url)
            raise GeoApiError(f"Erreur HTTP {e.code}: {e.reason}", e.code) from e
        except urllib.error.URLError as e:
            logger.error("URLError %s – %s", e.reason, url)
            raise GeoApiError(f"Erreur réseau : {e.reason}") from e
        except json.JSONDecodeError as e:
            logger.error("JSON invalide reçu de %s – %s", url, e)
            raise GeoApiError("Réponse JSON invalide") from e

    # -----------------------------------------------------------------
    def search_entities(self, entity_type: str, text: str) -> List[GeoEntity]:
        """Recherche d’entités par texte (min 2 caractères)."""
        if len(text) < 2:
            logger.debug("Texte trop court pour la recherche : %r", text)
            return []

        if entity_type not in ENDPOINTS:
            logger.debug("Type d'entité inconnu : %s", entity_type)
            raise InvalidEntityTypeError(entity_type)

        endpoint = ENDPOINTS[entity_type]
        fields   = FIELDS[entity_type]

        url = self._build_url(
            endpoint,
            {"nom": text, "fields": fields, "limit": "5"},
        )
        logger.info("Recherche %s pour %r → %s", entity_type, text, url)

        data = self._http_get(url, self.timeout_search)
        if not data:
            logger.warning("Aucun résultat pour %s : %r", entity_type, text)
            raise EntityNotFoundError(entity_type, text)

        return self._parse_entities(entity_type, data)

    # -----------------------------------------------------------------
    def fetch_entity_geometry(self, entity_type: str, code: str) -> QgsGeometry | None:
        """Récupère la géométrie (GeoJSON) d’une entité et la convertit en QgsGeometry."""
        if entity_type not in ENDPOINTS:
            raise InvalidEntityTypeError(entity_type)

        endpoint = ENDPOINTS[entity_type]
        url = self._build_url(
            f"{endpoint}/{code}",
            {"geometry": "contour", "format": "geojson"},
        )
        logger.info("Récupération géométrie %s → %s", entity_type, code)

        try:
            data = self._http_get(url, self.timeout_geom)
        except GeoApiError as exc:
            logger.error("Impossible de récupérer la géométrie : %s", exc)
            return None

        # Conversion via QGIS : on construit un FeatureCollection minimal
        fc = json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": data.get("geometry"),
                        "properties": {},
                    }
                ],
            }
        )
        feats = QgsJsonUtils.stringToFeatureList(fc)
        if feats:
            logger.debug("Géométrie convertie en QgsGeometry")
            return feats[0].geometry()
        logger.warning("Conversion GeoJSON → QgsGeometry a échoué")
        return None

    # -----------------------------------------------------------------
    @staticmethod
    def _parse_entities(entity_type: str, data: List[Dict[str, Any]]) -> List[GeoEntity]:
        """Transforme la réponse brute en objets dataclass."""
        if entity_type == "municipality":
            return [
                Municipality(
                    code=c["code"],
                    name=c["nom"],
                    department_code=c["codeDepartement"],
                )
                for c in data
            ]
        if entity_type == "department":
            return [
                Department(
                    code=c["code"],
                    name=c["nom"],
                    region_code=c["codeRegion"],
                )
                for c in data
            ]
        # region
        return [
            Region(code=c["code"], name=c["nom"])
            for c in data
        ]