"""
Stratégie API IGN
"""
from typing import List, Dict
from ..core.strategy import ApiStrategy

class IGNApiStrategy(ApiStrategy):
    """
    Strategy API IGN
    """

    def __init__(self):
        self.base_url = "https://apicarto.ign.fr/api"
        self.timeout_search = 5
        self.timeout_geom = 10

    def search(self, endpoint: str, text: str) -> List[Dict]:
        print(f"[IGN] search {endpoint} for '{text}'")
        return []

    def fetch_geometry(self, endpoint: str, code: str) -> Dict:
        print(f"[IGN] geometry {endpoint}/{code}")
        return {}

    def fetch_details(self, endpoint: str, code: str) -> Dict:
        print(f"[IGN] details {endpoint}/{code}")
        return {}