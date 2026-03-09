import pytest
import responses
from core.service import GeoService
from api.ign import IGNApiStrategy
from core.entities import Municipality

@responses.activate
def test_fetch_geometry():
    """Vérifie que la géométrie est correctement récupérée et décodée."""
    strategy = IGNApiStrategy()
    service = GeoService(strategy)
    endpoint = Municipality.API_ENDPOINT  # "communes"
    code = "75056"
    url = f"{strategy.base_url}/{endpoint}/{code}/geometry"
    mock_geom = {"type": "Polygon", "coordinates": []}
    responses.add(responses.GET, url, json=mock_geom, status=200)

    geometry = service.fetch_entity_geometry(Municipality, code)
    assert geometry == mock_geom

@responses.activate
def test_fetch_details():
    """Vérifie que les détails d'une entité sont correctement récupérés."""
    strategy = IGNApiStrategy()
    service = GeoService(strategy)
    endpoint = Municipality.API_ENDPOINT
    code = "75056"
    url = f"{strategy.base_url}/{endpoint}/{code}"
    mock_details = {"code": code, "nom": "Paris", "departement": {"code": "75"}}
    responses.add(responses.GET, url, json=mock_details, status=200)

    details = service.get_entity_details(Municipality, code)
    # La stratégie renvoie le JSON brut, le service le transmet tel quel
    assert details == mock_details
