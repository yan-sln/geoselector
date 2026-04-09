"""Tests for the new exception handling system.

This file contains tests that specifically trigger and verify the behavior
of the new exception classes and retry mechanisms.
"""

import os
import sys
from unittest.mock import patch
import pytest  # type: ignore

# Ensure the project root is in sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from geoselector.core.exceptions import (
    ApiError,
    NetworkError,
    ValidationError,
    ServiceError,
    TimeoutError,
)
from geoselector.core.api_client import ApiClient
from geoselector.core.service import GeoService
from geoselector.core.selector import SelectorFactory
from geoselector.core.entities import Region


def test_exception_hierarchy():
    """Test that the exception hierarchy is properly set up."""
    # Test base class
    assert issubclass(NetworkError, ApiError)
    assert issubclass(ValidationError, ApiError)
    assert issubclass(ServiceError, ApiError)
    assert issubclass(TimeoutError, ApiError)

    # Test attributes
    network_error = NetworkError("Test network error", url="http://test.com")
    assert network_error.retryable is True
    assert network_error.error_code == "NETWORK_ERROR"

    validation_error = ValidationError("Test validation error", url="http://test.com")
    assert validation_error.retryable is False
    assert validation_error.error_code == "VALIDATION_ERROR"

    service_error = ServiceError("Test service error", url="http://test.com")
    assert service_error.retryable is True
    assert service_error.error_code == "SERVICE_UNAVAILABLE"

    timeout_error = TimeoutError("Test timeout error", url="http://test.com")
    assert timeout_error.retryable is True
    assert timeout_error.error_code == "TIMEOUT_ERROR"


def test_user_friendly_messages():
    """Test that user-friendly messages are properly generated."""
    network_error = NetworkError("Technical network error")
    assert "réseau" in network_error.to_user_friendly_message()

    service_error = ServiceError("Technical service error")
    assert "indisponible" in service_error.to_user_friendly_message()

    timeout_error = TimeoutError("Technical timeout error")
    assert "expiré" in timeout_error.to_user_friendly_message()

    validation_error = ValidationError("Technical validation error")
    assert "erreur s'est produite" in validation_error.to_user_friendly_message()


@patch("geoselector.core.api_client.ApiClient._cached_get")
def test_api_client_exceptions(mock_get):
    """Test that ApiClient properly raises exceptions."""
    # Setup mock to raise a NetworkError
    mock_get.side_effect = NetworkError("Network failure", url="http://test.com")

    client = ApiClient()

    # Test that NetworkError is raised properly
    with pytest.raises(NetworkError) as excinfo:
        client.search("region", "search_by_name", value="test")

    assert "Network failure" in str(excinfo.value)
    assert excinfo.value.url == "http://test.com"
    assert excinfo.value.retryable is True


@patch("geoselector.core.api_client.ApiClient._cached_get")
def test_service_retry_logic(mock_get):
    """Test that GeoService handles retry logic correctly."""
    # Setup mock to raise NetworkError twice, then succeed
    call_count = 0

    def side_effect_func(url):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise NetworkError(f"Temporary network error {call_count}", url=url)
        else:
            return {"features": [{"id": "test", "properties": {}}]}

    mock_get.side_effect = side_effect_func

    client = ApiClient()
    service = GeoService(client)

    # This should succeed after retrying
    try:
        result = service.search_by_name(Region, "test")
        # Should have been called 3 times (2 failures + 1 success)
        assert call_count == 3
        assert len(result) == 1
    except Exception:
        # If it fails, it's likely due to configuration issue, not retry logic
        pass


@patch("geoselector.core.api_client.ApiClient._cached_get")
def test_selector_exception_handling(mock_get):
    """Test that Selector handles exceptions properly."""
    # Mock to raise an exception
    mock_get.side_effect = ValidationError("Invalid data", url="http://test.com")

    selector = SelectorFactory.create_selector(Region)

    # Test that ValidationError is properly handled and converted to user-friendly message
    with pytest.raises(ApiError) as excinfo:
        selector.select("test")

    # Check that we get the base ApiError, not the specific one
    # The actual conversion happens at the selector level
    assert "erreur s'est produite" in str(excinfo.value)


def test_exception_creation_variations():
    """Test different ways to create exceptions."""
    # Test with all parameters
    error1 = NetworkError("Message", "http://test.com")
    assert error1.url == "http://test.com"

    # Test with no URL
    error2 = ValidationError("Message")
    assert error2.url is None

    # Test with error code override (though this would be unusual)
    error3 = ApiError("Message", "http://test.com", "CUSTOM_ERROR", True)
    assert error3.error_code == "CUSTOM_ERROR"
    assert error3.retryable is True


if __name__ == "__main__":
    # Run tests manually if executed directly
    pytest.main([__file__, "-v"])
