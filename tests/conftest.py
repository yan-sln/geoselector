import pytest
from api.ign import IGNApiStrategy
from api.gouvfr import GouvFrApiStrategy
from core.registry import EntityRegistry

@pytest.fixture(autouse=True)
def clear_caches():
    """Nettoie le cache LRU entre chaque test pour les stratégies."""
    IGNApiStrategy().clear_cache()
    GouvFrApiStrategy().clear_cache()
    yield

@pytest.fixture(autouse=True)
def clear_registry():
    """Réinitialise le registre d'entités entre chaque test."""
    EntityRegistry._registry.clear()
    yield
