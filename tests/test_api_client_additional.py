"""Additional tests for the Confluence API client."""

import pytest
import httpx
import base64
from unittest.mock import AsyncMock, patch, MagicMock

from src.confluence_mcp.api_client import ConfluenceApiClient, get_client
from src.confluence_mcp.models import ConfluenceError


@pytest.fixture
def api_client():
    """Create a test API client."""
    client = ConfluenceApiClient(
        base_url="https://test-confluence.atlassian.net",
        api_key="test-api-key",
        user_email="test@example.com"
    )
    return client


@pytest.mark.asyncio
async def test_put_successful_request(api_client):
    """Test a successful PUT request."""
    request_data = {"id": "456", "title": "Updated Page", "version": {"number": 2}}
    test_response = {"id": "456", "title": "Updated Page", "version": {"number": 2}}
    
    # Mock the client's put method
    api_client.client.put = AsyncMock(return_value=httpx.Response(
        status_code=200,
        content=httpx._content.encode_json(test_response),
        request=httpx.Request("PUT", "https://test-confluence.atlassian.net/wiki/rest/api/content/456")
    ))
    
    response = await api_client.put("content/456", request_data)
    assert response == test_response
    
    # Verify the call
    api_client.client.put.assert_called_once()
    
    # Clean up
    await api_client.close()


@pytest.mark.asyncio
async def test_delete_successful_request(api_client):
    """Test a successful DELETE request."""
    # Mock the client's delete method
    api_client.client.delete = AsyncMock(return_value=httpx.Response(
        status_code=204,
        content=b"",
        request=httpx.Request("DELETE", "https://test-confluence.atlassian.net/wiki/rest/api/content/456")
    ))
    
    response = await api_client.delete("content/456")
    assert response == {}
    
    # Verify the call
    api_client.client.delete.assert_called_once()
    
    # Clean up
    await api_client.close()


@pytest.mark.asyncio
async def test_authentication_headers():
    """Test that authentication headers are correctly set."""
    client = ConfluenceApiClient(
        base_url="https://test-confluence.atlassian.net",
        api_key="test-api-key",
        user_email="test@example.com"
    )
    
    # Check the authorization header
    expected_auth = base64.b64encode(b"test@example.com:test-api-key").decode()
    assert client.headers["Authorization"] == f"Basic {expected_auth}"
    
    # Check content type and accept headers
    assert client.headers["Content-Type"] == "application/json"
    assert client.headers["Accept"] == "application/json"
    
    # Clean up
    await client.close()


@pytest.mark.asyncio
@patch("src.confluence_mcp.api_client.settings")
async def test_get_client_factory(mock_settings):
    """Test the get_client factory function."""
    # Configure mock settings
    mock_settings.CONFLUENCE_URL = "https://test-confluence.atlassian.net"
    mock_settings.CONFLUENCE_API_KEY = "test-api-key"
    mock_settings.CONFLUENCE_USER_EMAIL = "test@example.com"
    
    # Get a client using the factory function
    client = get_client()
    
    # Verify the client was configured with settings
    assert client.base_url == "https://test-confluence.atlassian.net"
    assert client.api_key == "test-api-key"
    assert client.user_email == "test@example.com"
    
    # Clean up
    await client.close()


@pytest.mark.asyncio
@patch("src.confluence_mcp.api_client.httpx.AsyncClient.get")
async def test_network_error_handling(mock_get, api_client):
    """Test handling of network errors."""
    # Mock a network error
    mock_get.side_effect = httpx.RequestError("Connection error", request=MagicMock())
    
    # Test that the error is properly caught and wrapped
    with pytest.raises(ConfluenceError) as exc_info:
        await api_client.get("spaces")
    
    assert "Connection error" in exc_info.value.message
    assert exc_info.value.status_code == 0  # No HTTP status code for network errors
    
    # Clean up
    await api_client.close()
