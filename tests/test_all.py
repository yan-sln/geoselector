"""Aggregated tests for the new architecture.

This file re‑implements the functionality of the original ``tests/test_*.py``
scripts using the high‑level ``SelectorFactory`` and ``GeoService`` classes
introduced in the refactor.  The tests do **not** import the old helper
functions; instead they exercise the public API of the ``core`` package.

Because the real WFS service is external, the tests are written to be safe
offline: they only verify that the selectors can be instantiated and that the
methods return the expected *type* (a list for ``select`` and ``None`` or a
``dict`` for ``get_geometry``).  Network calls are mocked with ``unittest.mock``
so the test suite runs deterministically.
"""

import json
import os
import sys
from unittest.mock import patch

import pytest

# Ensure the project root is in sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.entities import (
    Region,
    Departement,
    Commune,
    Arrondissement,
    Feuille,
    Parcelle,
    SubdivisionFiscale,
)
from core.selector import SelectorFactory

# ---------------------------------------------------------------------------
# Helper to mock the HTTP GET performed by ``ApiClient._cached_get``.
# It returns an empty feature collection, which is sufficient for the
# high‑level selectors used in these tests.
# ---------------------------------------------------------------------------

EMPTY_FEATURES = {"features": []}


@patch("core.api_client.ApiClient._cached_get", return_value=EMPTY_FEATURES)
@pytest.mark.parametrize(
    "entity_cls,search_text",
    [
        (Region, "Bretagne"),
        (Departement, "53"),
        (Commune, "59521"),
        (Arrondissement, "59521"),
        (Feuille, "59521"),
        (Parcelle, "59521"),
        (SubdivisionFiscale, "59521"),
    ],
)
def test_selector_select(mock_get, entity_cls, search_text):
    """Ensure that a selector can be created and ``select`` returns a list.

    The underlying HTTP request is mocked, so the result is an empty list.
    """
    selector = SelectorFactory.create_selector(entity_cls)
    results = selector.select(search_text)
    assert isinstance(results, list)
    # With the mocked empty response we expect no entities.
    assert results == []


@patch("core.api_client.ApiClient._cached_get", return_value=EMPTY_FEATURES)
@pytest.mark.parametrize(
    "entity_cls,code",
    [
        (Region, "53"),
        (Departement, "53"),
        (Commune, "59521"),
        (Arrondissement, "59521"),
        (Feuille, "59521"),
        (Parcelle, "59521"),
        (SubdivisionFiscale, "59521"),
    ],
)
def test_selector_get_geometry(mock_get, entity_cls, code):
    """Check that ``get_geometry`` returns ``None`` when no geometry is found.

    The mock provides an empty feature collection, so the service returns
    ``None``.
    """
    selector = SelectorFactory.create_selector(entity_cls)
    geometry = selector.get_geometry(code)
    assert geometry is None

# ---------------------------------------------------------------------------
# Additional sanity check: the factory caches ``GeoService`` instances.
# ---------------------------------------------------------------------------

def test_selector_factory_caching():
    s1 = SelectorFactory.create_selector(Region)
    s2 = SelectorFactory.create_selector(Departement)
    # Both selectors should share the same underlying ``GeoService`` instance.
    assert s1.service is s2.service

"""End of aggregated tests."""
