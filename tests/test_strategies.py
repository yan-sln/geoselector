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
    # Mock of the IGN API response for the "communes" endpoint
    url = f"{ign_strategy.base_url}/communes"
    mock_body = [
        {"code": "75056", "nom": "Paris", "departement": {"code": "75"}, "region": {"code": "11"}}
    ]
    # Ensure query parameters are validated (none in this simple case)
    responses.add(responses.GET, url, json=mock_body, status=200, match_querystring=True)

    result = ign_strategy.search(endpoint="communes", text="Paris", limit=5)
    assert isinstance(result, list)
    assert result[0]["code"] == "75056"
    assert result[0]["name"] == "Paris"
@responses.activate
def test_ign_search_pagination(ign_strategy):
    """Recherche sur l'API IGN avec pagination (deux pages)."""
    url = f"{ign_strategy.base_url}/communes"
    # Première page retourne un résultat
    first_page = [{"code": "75056", "nom": "Paris", "departement": {"code": "75"}, "region": {"code": "11"}}]
    # Deuxième page retourne un autre résultat
    second_page = [{"code": "69001", "nom": "Lyon", "departement": {"code": "69"}, "region": {"code": "84"}}]
    responses.add(responses.GET, url, json=first_page, status=200, match_querystring=True)
    responses.add(responses.GET, url, json=second_page, status=200, match_querystring=True)

    result = ign_strategy.search(endpoint="communes", text="city", limit=2)
    assert isinstance(result, list)
    assert len(result) == 2
    codes = {item["code"] for item in result}
    assert codes == {"75056", "69001"}

@responses.activate
def test_gouvfr_search_error(gouvfr_strategy):
    """Gestion d'une réponse d'erreur HTTP (400) – la stratégie doit renvoyer []"""
    url = f"{gouvfr_strategy.base_url}/communes"
    responses.add(responses.GET, url, json={"error": "Bad request"}, status=400, match_querystring=True)

    result = gouvfr_strategy.search(endpoint="communes", text="Lyon")
    # En cas d’erreur, la stratégie renvoie une liste vide
    assert result == []
