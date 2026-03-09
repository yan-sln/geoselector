import pytest
import responses
from api.ign import IGNApiStrategy
from api.gouvfr import GouvFrApiStrategy

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture
def ign_strategy():
    return IGNApiStrategy()

@pytest.fixture
def gouvfr_strategy():
    return GouvFrApiStrategy()

# ----------------------------------------------------------------------
# Tests de recherche IGN
# ----------------------------------------------------------------------
@responses.activate
def test_ign_search_success(ign_strategy):
    # Mock de la réponse de l’API IGN pour le endpoint "communes"
    url = f"{ign_strategy.base_url}/communes"
    mock_body = [
        {"code": "75056", "nom": "Paris", "departement": {"code": "75"}, "region": {"code": "11"}}
    ]
    responses.add(responses.GET, url, json=mock_body, status=200)

    result = ign_strategy.search(endpoint="communes", text="Paris", limit=5)
    assert isinstance(result, list)
    assert result[0]["code"] == "75056"
    assert result[0]["name"] == "Paris"

@responses.activate
def test_gouvfr_search_error(gouvfr_strategy):
    url = f"{gouvfr_strategy.base_url}/communes"
    responses.add(responses.GET, url, json={"error": "Bad request"}, status=400)

    result = gouvfr_strategy.search(endpoint="communes", text="Lyon")
    # En cas d’erreur, la stratégie renvoie une liste vide
    assert result == []
