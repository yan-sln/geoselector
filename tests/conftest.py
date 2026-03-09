import pytest
from api.ign import IGNApiStrategy
from api.gouvfr import GouvFrApiStrategy

@pytest.fixture(autouse=True)
def clear_caches():
    """Nettoie le cache LRU entre chaque test pour les stratégies."""
    IGNApiStrategy().clear_cache()
    GouvFrApiStrategy().clear_cache()
    yield
