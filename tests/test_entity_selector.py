import pytest
import responses
from core.selector import EntitySelectorImpl
from core.service import GeoService
from api.ign import IGNApiStrategy
from core.entities import Municipality, Department, Region, Parcel, Section

@pytest.fixture
def selector():
    strategy = IGNApiStrategy()
    service = GeoService(strategy)
    return EntitySelectorImpl(Municipality, service)

@responses.activate
def test_select_returns_entities(selector):
    """Vérifie que le sélecteur retourne des instances de l'entité attendue."""
    endpoint = Municipality.API_ENDPOINT  # "communes"
    url = f"{selector.service.strategy.base_url}/{endpoint}"
    mock_data = [
        {"code": "75056", "nom": "Paris", "departement": {"code": "75"}, "region": {"code": "11"}}
    ]
    responses.add(responses.GET, url, json=mock_data, status=200)

    results = selector.select(text="Paris")
    assert len(results) == 1
    entity = results[0]
    assert isinstance(entity, Municipality)
    assert entity.code == "75056"
    assert entity.name == "Paris"
    assert entity.department_code == "75"

@responses.activate
def test_get_geometry_and_details(selector):
    """Vérifie que le sélecteur récupère géométrie et détails via le service."""
    code = "75056"
    # Geometry endpoint
    geom_url = f"{selector.service.strategy.base_url}/{Municipality.API_ENDPOINT}/{code}/geometry"
    mock_geom = {"type": "Polygon", "coordinates": []}
    responses.add(responses.GET, geom_url, json=mock_geom, status=200)
    # Details endpoint
    details_url = f"{selector.service.strategy.base_url}/{Municipality.API_ENDPOINT}/{code}"
    mock_details = {"code": code, "nom": "Paris", "departement": {"code": "75"}}
    responses.add(responses.GET, details_url, json=mock_details, status=200)

    geometry = selector.get_geometry(code)
    details = selector.get_details(code)
    assert geometry == mock_geom
    assert details == mock_details
