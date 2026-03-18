"""Aggregated tests for the new architecture.

This file re‑implements the functionality of the original ``tests/test_*.py``
scripts using the high‑level ``SelectorFactory`` and ``GeoService`` classes
introduced in the refactor.

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
    # Print output similar to original scripts
    print(f"{entity_cls.__name__}.select('{search_text}') =>", results)
    assert isinstance(results, list)
    # With the mocked empty response we expect no entities.
    assert results == []
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
    # Print output similar to original scripts
    print(f"{entity_cls.__name__}.get_geometry('{code}') =>", geometry)
    assert geometry is None
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

if __name__ == "__main__":
    # Demonstration reproducing the console outputs of the original test scripts
    from core.selector import SelectorFactory
    from core.entities import (
        Region,
        Departement,
        Commune,
        Arrondissement,
        Section,
        Feuille,
        Parcelle,
        SubdivisionFiscale,
    )

    # Region: search by name and by code, then geometry
    region_selector = SelectorFactory.create_selector(Region)
    region_by_name = region_selector.select('Bretagne')
    print('Résultat recherche par nom :', region_by_name)
    region_by_code = region_selector.select('53')
    print('Résultat recherche par code :', region_by_code)
    region_geom = region_selector.get_geometry('53')
    print('Géométrie de la région récupérée avec succès !' if region_geom else 'Échec de la récupération de la géométrie de la région.')

    # Departement: similar to region
    dep_selector = SelectorFactory.create_selector(Departement)
    dep_by_name = dep_selector.select('53')
    print('Département recherche par code :', dep_by_name)
    dep_geom = dep_selector.get_geometry('53')
    print('Géométrie récupérée avec succès !' if dep_geom else 'Échec de la récupération de la géométrie.')

    # Commune
    com_selector = SelectorFactory.create_selector(Commune)
    com_res = com_selector.select('59521')
    print('Commune recherche :', com_res)
    com_geom = com_selector.get_geometry('59521')
    print('Géométrie récupérée avec succès !' if com_geom else 'Échec de la récupération de la géométrie.')

    # Arrondissement
    arr_selector = SelectorFactory.create_selector(Arrondissement)
    arr_res = arr_selector.select('75056')
    print('Arrondissement recherche :', arr_res[:2])
    arr_geom = arr_selector.get_geometry('119')
    print('Géométrie récupérée avec succès !' if arr_geom else 'Échec de la récupération de la géométrie.')

    # Section
    se_selector = SelectorFactory.create_selector(Section)
    se_res = se_selector.select('59521')
    print('Section recherche :', se_res[:2])
    se_geom = se_selector.get_geometry('59521', 'ZC')
    print('Géométrie récupérée avec succès !' if se_geom else 'Échec de la récupération de la géométrie.')

    # Feuille
    fe_selector = SelectorFactory.create_selector(Feuille)
    fe_res = fe_selector.select('59521', 'ZC')
    print('Feuille recherche :', fe_res)
    fe_geom = fe_selector.get_geometry('59521','ZC','1')
    print('Géométrie récupérée avec succès !' if fe_geom else 'Échec de la récupération de la géométrie.')

    # Parcelle
    parc_selector = SelectorFactory.create_selector(Parcelle)
    parc_res = parc_selector.select('59521', 'ZC')
    print('Parcelles listées :', parc_res[:2])
    parc_geom = parc_selector.get_geometry('parcelle.43803455')
    print('Géométrie récupérée avec succès !' if parc_geom else 'Échec de la récupération de la géométrie.')

    # Subdivision Fiscale
    sub_selector = SelectorFactory.create_selector(SubdivisionFiscale)
    sub_res = sub_selector.select('59521000ZC0063')
    print('Subdivision fiscale recherche :', sub_res)
    sub_geom = sub_selector.get_geometry('5411001')
    # sub_res[0].get_geometry()
    print('Géométrie récupérée avec succès !' if sub_geom else 'Échec de la récupération de la géométrie.')
