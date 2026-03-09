import pytest
import responses
from core.service import GeoService
from api.ign import IGNApiStrategy
from core.entities import Municipality

@responses.activate
def test_fetch_geometry():
    """Vérifie que la géométrie est correctement récupérée et décodée, et que le cache LRU fonctionne."""
    strategy = IGNApiStrategy()
    service = GeoService(strategy)
    endpoint = Municipality.API_ENDPOINT  # "communes"
    code = "75056"
    url = f"{strategy.base_url}/{endpoint}/{code}/geometry"
    mock_geom = {"type": "Polygon", "coordinates": []}
    # First request
    responses.add(responses.GET, url, json=mock_geom, status=200, match_querystring=True)

    geometry = service.fetch_entity_geometry(Municipality, code)
    assert geometry == mock_geom
    # Second call should hit cache – no additional HTTP request
    geometry_cached = service.fetch_entity_geometry(Municipality, code)
    assert geometry_cached == mock_geom
    # Verify only one request was made
    assert len(responses.calls) == 1

@responses.activate
def test_fetch_details():
    """Vérifie que les détails d'une entité sont correctement récupérés."""
    strategy = IGNApiStrategy()
    service = GeoService(strategy)
    endpoint = Municipality.API_ENDPOINT
    code = "75056"
    url = f"{strategy.base_url}/{endpoint}/{code}"
    mock_details = {"code": code, "nom": "Paris", "departement": {"code": "75"}}
    responses.add(responses.GET, url, json=mock_details, status=200, match_querystring=True)

    details = service.get_entity_details(Municipality, code)
    # La stratégie renvoie le JSON brut, le service le transmet tel comment
    assert details == mock_details

@responses.activate
def test_fetch_details_error():
    """Gestion d'une réponse d'erreur HTTP (500) lors de la récupération des détails."""
    strategy = IGNApiStrategy()
    service = GeoService(strategy)
    endpoint = Municipality.API_ENDPOINT
    code = "99999"
    url = f"{strategy.base_url}/{endpoint}/{code}"
    responses.add(responses.GET, url, json={"error": "Server error"}, status=500, match_querystring=True)

    details = service.get_entity_details(Municipality, code)
    # En cas d'erreur, la stratégie renvoie {} (voir ApiStrategy._cached_fetch)
    assert details == {}
