"""Tests for the Confluence API client."""

import pytest
import httpx
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.confluence_mcp.api_client import ConfluenceApiClient
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
async def test_api_client_initialization(api_client):
    """Test the API client initialization."""
    assert api_client.base_url == "https://test-confluence.atlassian.net"
    assert api_client.api_key == "test-api-key"
    assert api_client.user_email == "test@example.com"
    assert api_client.api_url == "https://test-confluence.atlassian.net/wiki/rest/api"
    
    # Clean up
    await api_client.close()


@pytest.mark.asyncio
async def test_get_successful_request(api_client):
    """Test a successful GET request."""
    test_response = {"results": [{"id": "123", "name": "Test Space"}]}
    
    # Mock the client's get method
    mock_response = httpx.Response(
        status_code=200,
        content=json.dumps(test_response).encode(),
        request=httpx.Request("GET", "https://test-confluence.atlassian.net/wiki/rest/api/spaces")
    )
    api_client.client.get = AsyncMock(return_value=mock_response)
    
    response = await api_client.get("spaces", {"limit": 10})
    assert response == test_response
    
    # Verify the call
    api_client.client.get.assert_called_once()
    
    # Clean up
    await api_client.close()


@pytest.mark.asyncio
async def test_get_error_response(api_client):
    """Test handling of an error response."""
    error_response = {"message": "Not found", "details": "The requested resource was not found"}
    
    # Mock the client's get method
    mock_response = httpx.Response(
        status_code=404,
        content=json.dumps(error_response).encode(),
        request=httpx.Request("GET", "https://test-confluence.atlassian.net/wiki/rest/api/spaces/INVALID")
    )
    api_client.client.get = AsyncMock(return_value=mock_response)
    
    with pytest.raises(ConfluenceError) as exc_info:
        await api_client.get("spaces/INVALID")
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "Not found"
    assert exc_info.value.detailed_message == "The requested resource was not found"
    
    # Clean up
    await api_client.close()


@pytest.mark.asyncio
async def test_post_successful_request(api_client):
    """Test a successful POST request."""
    request_data = {"title": "New Page", "spaceId": "123", "status": "current"}
    test_response = {"id": "456", "title": "New Page", "spaceId": "123"}
    
    # Mock the client's post method
    mock_response = httpx.Response(
        status_code=200,
        content=json.dumps(test_response).encode(),
        request=httpx.Request("POST", "https://test-confluence.atlassian.net/wiki/rest/api/pages")
    )
    api_client.client.post = AsyncMock(return_value=mock_response)
    
    response = await api_client.post("content", request_data)
    assert response == test_response
    
    # Verify the call
    api_client.client.post.assert_called_once()
    
    # Clean up
    await api_client.close()


@pytest.mark.asyncio
async def test_put_successful_request(api_client):
    """Test a successful PUT request."""
    request_data = {"id": "456", "title": "Updated Page", "version": {"number": 2}}
    test_response = {"id": "456", "title": "Updated Page", "version": {"number": 2}}
    
    # Mock the client's put method
    mock_response = httpx.Response(
        status_code=200,
        content=json.dumps(test_response).encode(),
        request=httpx.Request("PUT", "https://test-confluence.atlassian.net/wiki/rest/api/content/456")
    )
    api_client.client.put = AsyncMock(return_value=mock_response)
    
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
    mock_response = httpx.Response(
        status_code=204,
        content=b"",
        request=httpx.Request("DELETE", "https://test-confluence.atlassian.net/wiki/rest/api/content/456")
    )
    api_client.client.delete = AsyncMock(return_value=mock_response)
    
    response = await api_client.delete("content/456")
    assert response == {}
    
    # Verify the call
    api_client.client.delete.assert_called_once()
    
    # Clean up
    await api_client.close()


@pytest.mark.asyncio
async def test_network_error_handling(api_client):
    """Test handling of network errors."""
    # Mock a network error
    api_client.client.get = AsyncMock(side_effect=httpx.RequestError("Connection error", request=MagicMock()))
    
    # Test that the error is properly caught and wrapped
    with pytest.raises(ConfluenceError) as exc_info:
        await api_client.get("spaces")
    
    assert "Connection error" in exc_info.value.message
    assert exc_info.value.status_code == 0  # No HTTP status code for network errors
    
    # Clean up
    await api_client.close()
