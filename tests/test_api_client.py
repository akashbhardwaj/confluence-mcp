"""Comprehensive tests for the Confluence API client.

This module consolidates all API client tests into a single comprehensive test suite,
covering basic operations, error handling, authentication, retry mechanisms, and pagination.
"""

import pytest
import httpx
import json
import base64
from unittest.mock import AsyncMock, MagicMock, patch

from src.confluence_mcp.api_client import ConfluenceApiClient, get_client, retry_on_connection_error
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


@pytest.fixture
def mock_response():
    """Create a mock HTTP response helper."""
    def _create_response(status_code: int, data: dict, url: str = "https://test-confluence.atlassian.net/wiki/rest/api/test"):
        return httpx.Response(
            status_code=status_code,
            content=json.dumps(data).encode(),
            request=httpx.Request("GET", url)
        )
    return _create_response


class TestApiClientInitialization:
    """Test API client initialization and configuration."""
    
    @pytest.mark.asyncio
    async def test_basic_initialization(self, api_client):
        """Test basic API client initialization."""
        assert api_client.base_url == "https://test-confluence.atlassian.net"
        assert api_client.api_key == "test-api-key"
        assert api_client.user_email == "test@example.com"
        assert api_client.api_url == "https://test-confluence.atlassian.net/wiki/rest/api"
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_initialization_with_custom_params(self):
        """Test API client initialization with custom parameters."""
        client = ConfluenceApiClient(
            base_url="https://custom.atlassian.net",
            api_key="custom_api_key",
            user_email="custom@example.com",
            timeout=60.0,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)
        )
        
        assert client.base_url == "https://custom.atlassian.net"
        assert client.api_key == "custom_api_key"
        assert client.user_email == "custom@example.com"
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_authentication_headers(self):
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
        
        await client.close()


class TestHttpMethods:
    """Test HTTP methods (GET, POST, PUT, DELETE)."""
    
    @pytest.mark.asyncio
    async def test_get_successful_request(self, api_client, mock_response):
        """Test a successful GET request."""
        test_response = {"results": [{"id": "123", "name": "Test Space"}]}
        
        api_client.client.get = AsyncMock(return_value=mock_response(200, test_response))
        
        response = await api_client.get("spaces", {"limit": 10})
        assert response == test_response
        
        # Verify the call
        api_client.client.get.assert_called_once()
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_post_successful_request(self, api_client, mock_response):
        """Test a successful POST request."""
        request_data = {"title": "New Page", "spaceId": "123", "status": "current"}
        test_response = {"id": "456", "title": "New Page", "spaceId": "123"}
        
        api_client.client.post = AsyncMock(return_value=mock_response(200, test_response))

        response = await api_client.post("content", request_data)
        assert response == test_response
        
        # Verify the call
        api_client.client.post.assert_called_once()
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_put_successful_request(self, api_client, mock_response):
        """Test a successful PUT request."""
        request_data = {"id": "456", "title": "Updated Page", "version": {"number": 2}}
        test_response = {"id": "456", "title": "Updated Page", "version": {"number": 2}}
        
        api_client.client.put = AsyncMock(return_value=mock_response(200, test_response))
        
        response = await api_client.put("content/456", request_data)
        assert response == test_response
        
        # Verify the call
        api_client.client.put.assert_called_once()
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_delete_successful_request(self, api_client):
        """Test a successful DELETE request."""
        api_client.client.delete = AsyncMock(return_value=httpx.Response(
            status_code=204,
            content=b"",
            request=httpx.Request("DELETE", "https://test-confluence.atlassian.net/wiki/rest/api/content/456")
        ))
        
        response = await api_client.delete("content/456")
        assert response == {}
        
        # Verify the call
        api_client.client.delete.assert_called_once()
        
        await api_client.close()


class TestErrorHandling:
    """Test error handling and exception scenarios."""
    
    @pytest.mark.asyncio
    async def test_get_error_response(self, api_client):
        """Test handling of an error response."""
        error_response = {"message": "Not found", "details": "The requested resource was not found"}
        
        api_client.client.get = AsyncMock(return_value=httpx.Response(
            status_code=404,
            content=json.dumps(error_response).encode(),
            request=httpx.Request("GET", "https://test-confluence.atlassian.net/wiki/rest/api/spaces/INVALID")
        ))
        
        with pytest.raises(ConfluenceError) as exc_info:
            await api_client.get("spaces/INVALID")

        assert exc_info.value.status_code == 404
        assert exc_info.value.message == "Not found"
        assert exc_info.value.detailed_message == "The requested resource was not found"
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, api_client):
        """Test handling of network errors."""
        # Mock a network error
        api_client.client.get = AsyncMock(side_effect=httpx.RequestError("Connection error", request=MagicMock()))
        
        # Test that the error is properly caught and wrapped
        with pytest.raises(ConfluenceError) as exc_info:
            await api_client.get("spaces")
        
        assert "Connection error" in exc_info.value.message
        assert exc_info.value.status_code == 0  # No HTTP status code for network errors
        
        await api_client.close()


class TestRetryMechanism:
    """Test retry mechanism for connection errors."""
    
    @pytest.mark.asyncio
    @patch('src.confluence_mcp.api_client.asyncio.sleep')
    async def test_retry_on_connection_error_success(self, mock_sleep):
        """Test retry mechanism on connection errors with eventual success."""
        # Create a test method with the retry decorator
        call_count = 0
        
        async def mock_operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise httpx.RequestError("Connection error", request=httpx.Request("GET", "https://test.atlassian.net"))
            return {"success": True}
        
        # Apply the decorator
        @retry_on_connection_error(max_retries=3, retry_delay=0.1)
        async def test_method():
            return await mock_operation()
        
        # Call the method
        result = await test_method()
        
        # Verify retry behavior
        assert call_count == 3
        assert mock_sleep.call_count == 2  # Sleep should be called twice for 2 retries
        assert result == {"success": True}
    
    @pytest.mark.asyncio
    @patch('src.confluence_mcp.api_client.asyncio.sleep')
    async def test_retry_exhaustion(self, mock_sleep):
        """Test that retry mechanism eventually gives up after max retries."""
        call_count = 0
        
        async def mock_operation():
            nonlocal call_count
            call_count += 1
            raise httpx.RequestError("Persistent connection error", request=httpx.Request("GET", "https://test.atlassian.net"))
        
        # Apply the decorator
        @retry_on_connection_error(max_retries=3, retry_delay=0.1)
        async def test_method():
            return await mock_operation()
        
        # Call the method and expect it to eventually raise the error
        with pytest.raises(httpx.RequestError):
            await test_method()
        
        # Verify retry behavior
        assert call_count == 4  # Initial + 3 retries
        assert mock_sleep.call_count == 3  # Sleep should be called 3 times for 3 retries


class TestPagination:
    """Test pagination functionality."""
    
    @pytest.mark.asyncio
    async def test_fetch_all_pages_single_page(self, api_client, mock_response):
        """Test fetch_all_pages with single page of results."""
        test_response = {
            "results": [{"id": "1", "title": "Page 1"}, {"id": "2", "title": "Page 2"}],
            "size": 2,
            "_links": {}  # No next link indicates last page
        }
        
        api_client.client.get = AsyncMock(return_value=mock_response(200, test_response))
        
        results = await api_client.fetch_all_pages("content", {"limit": 10})
        
        assert len(results) == 2
        assert results[0]["id"] == "1"
        assert results[1]["id"] == "2"
        
        # Should only make one call since there's no next page
        api_client.client.get.assert_called_once()
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_fetch_all_pages_multiple_pages(self, api_client):
        """Test fetch_all_pages with multiple pages of results."""
        # First page response
        first_response = httpx.Response(
            status_code=200,
            content=json.dumps({
                "results": [{"id": "1", "title": "Page 1"}, {"id": "2", "title": "Page 2"}],
                "size": 2,
                "_links": {"next": "/wiki/rest/api/content?start=2&limit=2"}
            }).encode(),
            request=httpx.Request("GET", "https://test-confluence.atlassian.net/wiki/rest/api/content")
        )
        
        # Second page response (last page)
        second_response = httpx.Response(
            status_code=200,
            content=json.dumps({
                "results": [{"id": "3", "title": "Page 3"}],
                "size": 1,
                "_links": {}  # No next link
            }).encode(),
            request=httpx.Request("GET", "https://test-confluence.atlassian.net/wiki/rest/api/content")
        )
        
        api_client.client.get = AsyncMock(side_effect=[first_response, second_response])
        
        results = await api_client.fetch_all_pages("content", {"limit": 2})
        
        assert len(results) == 3
        assert results[0]["id"] == "1"
        assert results[1]["id"] == "2"
        assert results[2]["id"] == "3"
        
        # Should make two calls
        assert api_client.client.get.call_count == 2
        
        await api_client.close()
    
    @pytest.mark.asyncio
    async def test_fetch_all_pages_with_max_pages(self, api_client):
        """Test fetch_all_pages with max_pages limit."""
        # First page response
        first_response = httpx.Response(
            status_code=200,
            content=json.dumps({
                "results": [{"id": "1", "title": "Page 1"}, {"id": "2", "title": "Page 2"}],
                "size": 2,
                "_links": {"next": "/wiki/rest/api/content?start=2&limit=2"}
            }).encode(),
            request=httpx.Request("GET", "https://test-confluence.atlassian.net/wiki/rest/api/content")
        )
        
        api_client.client.get = AsyncMock(return_value=first_response)
        
        # Limit to 1 page only
        results = await api_client.fetch_all_pages("content", {"limit": 2}, max_pages=1)
        
        assert len(results) == 2
        assert results[0]["id"] == "1"
        assert results[1]["id"] == "2"
        
        # Should only make one call due to max_pages limit
        api_client.client.get.assert_called_once()
        
        await api_client.close()


class TestFactoryFunction:
    """Test the get_client factory function."""
    
    @pytest.mark.asyncio
    @patch("src.confluence_mcp.api_client.settings")
    async def test_get_client_factory(self, mock_settings):
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
        
        await client.close()


if __name__ == "__main__":
    pytest.main([__file__])
