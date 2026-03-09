import os
import subprocess
import pytest

from core.registry import EntityRegistry

# Proxy URL should be provided via an environment variable to avoid committing secrets.
PROXY = os.getenv("GOUVFR_PROXY")

@pytest.mark.parametrize("entity_cls", EntityRegistry.list_entities())
def test_endpoint_availability(entity_cls):
    """Check that the public Geo API endpoint for each GeoEntity returns HTTP 200.

    The request is performed through the configured proxy. If the proxy is not set,
    the test is skipped to avoid false failures in environments without network access.
    """
    if not PROXY:
        pytest.skip("GOUVFR_PROXY environment variable not set; skipping endpoint availability test.")

    endpoint = getattr(entity_cls, "API_ENDPOINT", "")
    assert endpoint, f"{entity_cls.__name__} does not define a non‑empty API_ENDPOINT"

    url = f"https://geo.api.gouv.fr/{endpoint}"
    curl_cmd = [
        "curl",
        "-x", PROXY,
        "-s", "-o", "/dev/null", "-w", "%{http_code}",
        url,
    ]
    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    http_code = result.stdout.strip()
    assert http_code == "200", f"Endpoint {endpoint} returned HTTP {http_code}"
