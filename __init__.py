# -*- coding: utf-8 -*-
"""
Package public API – expose les classes principales.
"""

from pathlib import Path

# Chemin absolu du répertoire du package (pour charger config.yaml)
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

# Import du logger (évalué une seule fois)
from .logging_config import configure_logging

# Export des classes utiles
from .core.geo_service import GeoDataService
from .selectors.entity_selector import EntitySelector
from .feature_selectors.entity_feature_selector import EntityFeatureSelector
from .utils.geometry_utils import GeometryUtils

__all__ = [
    "GeoDataService",
    "EntitySelector",
    "EntityFeatureSelector",
    "GeometryUtils",
]