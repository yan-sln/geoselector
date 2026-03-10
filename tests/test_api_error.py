import pytest
from unittest.mock import patch
import requests

from core.strategy import ApiStrategy, ApiError


class DummyStrategy(ApiStrategy):
    """Minimal concrete implementation of :class:`ApiStrategy` for testing.

    Only the abstract ``search`` method is implemented to satisfy the ABC.
    The method delegates to ``_paged_fetch`` with a trivial formatter that
    returns the raw data unchanged.
    """

    def search(self, endpoint: str, text: str, limit: int | None = None, page: int = 1):
        return self._paged_fetch(endpoint, text, limit=limit, page=page, formatter=lambda x: x)


def test_request_raises_api_error():
    """Ensure that a ``requests.RequestException`` is wrapped in ``ApiError``.

    The ``requests.Session.request`` method is patched to raise a
    ``RequestException``. The test verifies that calling ``_request`` on the
    strategy raises the custom ``ApiError`` with the original exception attached.
    """
    strategy = DummyStrategy()
    with patch.object(strategy.session, "request", side_effect=requests.RequestException("network error")):
        with pytest.raises(ApiError) as exc_info:
            strategy._request("GET", "https://example.com")
        # The original exception should be stored on the ApiError instance
        assert isinstance(exc_info.value.original_exception, requests.RequestException)
        assert "network error" in str(exc_info.value.original_exception)
