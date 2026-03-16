from functools import lru_cache
from typing import Any

# Cache LRU global pour les géométries
@lru_cache(maxsize=256)
def cached_fetch_geometry(strategy_name: str, endpoint: str, code: str) -> dict:
    """
    Fonction simulée qui pourrait appeler la stratégie.
    Pour l'exemple, on ne fait rien ici.
    """
    raise NotImplementedError("Ce serait utilisé dans GeoRepository.")