"""Tests for enhanced API client features."""

import sys
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch, call
import unittest
import httpx

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.confluence_mcp.api_client import ConfluenceApiClient
from src.confluence_mcp.models import ConfluenceError


class TestEnhancedApiClient(unittest.IsolatedAsyncioTestCase):
    """Tests for enhanced API client features."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a client with test values
        self.client = ConfluenceApiClient(
            base_url="https://test.atlassian.net",
            api_key="test_api_key",
            user_email="test@example.com"
        )
        
        # Replace the HTTP client with a mock
        self.client.client = MagicMock()
        self.client.client.get = AsyncMock()
        self.client.client.post = AsyncMock()
    
    @patch('src.confluence_mcp.api_client.httpx.AsyncClient')
    def test_client_initialization_with_params(self, mock_async_client):
        """Test API client initialization with custom parameters."""
        client = ConfluenceApiClient(
            base_url="https://custom.atlassian.net",
            api_key="custom_api_key",
            user_email="custom@example.com",
            timeout=60.0,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)
        )
        
        # Verify the client was created with custom parameters
        mock_async_client.assert_called_once()
        args, kwargs = mock_async_client.call_args
        
        self.assertEqual(kwargs['timeout'], 60.0)
        self.assertEqual(kwargs['limits'].max_connections, 20)
        self.assertEqual(kwargs['limits'].max_keepalive_connections, 10)
    
    async def test_fetch_all_pages_single_page(self):
        """Test fetching all pages when there's only one page of results."""
        # Setup mock response for a single page
        self.client.get = AsyncMock(return_value={
            "results": [{"id": "1"}, {"id": "2"}],
            "_links": {}  # No 'next' link
        })
        
        # Call the method
        results = await self.client.fetch_all_pages("spaces", {"limit": 10})
        
        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "1")
        self.assertEqual(results[1]["id"], "2")
        
        # Verify the client.get was called correctly
        self.client.get.assert_called_once_with("spaces", {"limit": 10, "start": 0})
    
    async def test_fetch_all_pages_multiple_pages(self):
        """Test fetching all pages when there are multiple pages."""
        # Setup mock responses for pagination
        self.client.get = AsyncMock()
        
        # Reset the mock's call count and side effect
        self.client.get.reset_mock()
        self.client.get.side_effect = None
        
        # Set up the responses for different calls
        responses = [
            # First page
            {
                "results": [{"id": "1"}, {"id": "2"}],
                "_links": {"next": "/spaces?start=2&limit=2"}
            },
            # Second page
            {
                "results": [{"id": "3"}, {"id": "4"}],
                "_links": {"next": "/spaces?start=4&limit=2"}
            },
            # Third page
            {
                "results": [{"id": "5"}],
                "_links": {}  # No 'next' link
            }
        ]
        
        # Configure the mock to return different responses for each call
        self.client.get.side_effect = responses
        
        # Call the method
        results = await self.client.fetch_all_pages("spaces", {"limit": 2})
        
        # Verify the results
        self.assertEqual(len(results), 5)
        self.assertEqual([r["id"] for r in results], ["1", "2", "3", "4", "5"])
        
        # Verify the calls
        self.assertEqual(self.client.get.call_count, 3)
        
        # Verify the parameters for each call
        call_args_list = self.client.get.call_args_list
        self.assertEqual(call_args_list[0][0][0], "spaces")
        self.assertEqual(call_args_list[0][0][1], {"limit": 2, "start": 0})
        
        self.assertEqual(call_args_list[1][0][0], "spaces")
        self.assertEqual(call_args_list[1][0][1], {"limit": 2, "start": 2})
        
        self.assertEqual(call_args_list[2][0][0], "spaces")
        self.assertEqual(call_args_list[2][0][1], {"limit": 2, "start": 4})
    
    async def test_fetch_all_pages_with_max_pages(self):
        """Test fetching all pages with a maximum page limit."""
        # Setup mock responses for pagination
        self.client.get = AsyncMock()
        self.client.get.side_effect = [
            # First page
            {
                "results": [{"id": "1"}, {"id": "2"}],
                "_links": {"next": "/spaces?start=2&limit=2"}
            },
            # Second page
            {
                "results": [{"id": "3"}, {"id": "4"}],
                "_links": {"next": "/spaces?start=4&limit=2"}
            }
        ]
        
        # Call the method with max_pages=2
        results = await self.client.fetch_all_pages("spaces", {"limit": 2}, max_pages=2)
        
        # Verify the results (should only have the first 4 items)
        self.assertEqual(len(results), 4)
        self.assertEqual([r["id"] for r in results], ["1", "2", "3", "4"])
        
        # Verify the client.get was called correctly for each page (only 2 pages)
        self.assertEqual(self.client.get.call_count, 2)
    
    @patch('src.confluence_mcp.api_client.asyncio.sleep')
    async def test_retry_on_connection_error(self, mock_sleep):
        """Test retry mechanism on connection errors."""
        # Create a test method with the retry decorator
        from src.confluence_mcp.api_client import retry_on_connection_error
        
        # Mock HTTP error that should trigger retries
        self.client.client.get.side_effect = [
            httpx.RequestError("Connection error", request=httpx.Request("GET", "https://test.atlassian.net")),
            httpx.RequestError("Connection error", request=httpx.Request("GET", "https://test.atlassian.net")),
            # Third time succeeds
            httpx.Response(200, json={"success": True})
        ]
        
        # Apply the decorator to a test method
        @retry_on_connection_error(max_retries=3, retry_delay=0.1)
        async def test_method():
            return await self.client.client.get("https://test.atlassian.net")
        
        # Call the method
        result = await test_method()
        
        # Verify retry behavior
        self.assertEqual(self.client.client.get.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # Sleep should be called twice for 2 retries
        self.assertEqual(result.json(), {"success": True})
    
    @patch('src.confluence_mcp.api_client.asyncio.sleep')
    async def test_retry_exhaustion(self, mock_sleep):
        """Test that retry mechanism eventually gives up after max retries."""
        # Create a test method with the retry decorator
        from src.confluence_mcp.api_client import retry_on_connection_error
        
        # Mock HTTP error that will always fail
        error = httpx.RequestError("Persistent connection error", request=httpx.Request("GET", "https://test.atlassian.net"))
        self.client.client.get.side_effect = error
        
        # Apply the decorator to a test method
        @retry_on_connection_error(max_retries=3, retry_delay=0.1)
        async def test_method():
            return await self.client.client.get("https://test.atlassian.net")
        
        # Call the method and expect it to eventually raise the error
        with self.assertRaises(httpx.RequestError):
            await test_method()
        
        # Verify retry behavior
        self.assertEqual(self.client.client.get.call_count, 4)  # Initial + 3 retries
        self.assertEqual(mock_sleep.call_count, 3)  # Sleep should be called 3 times for 3 retries


if __name__ == '__main__':
    unittest.main()
