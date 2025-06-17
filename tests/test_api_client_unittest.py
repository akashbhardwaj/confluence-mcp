"""Tests for the Confluence API client using unittest."""

import sys
import os
import httpx
import json
from unittest.mock import AsyncMock, MagicMock, patch
import unittest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.confluence_mcp.api_client import ConfluenceApiClient
from src.confluence_mcp.models import ConfluenceError


class TestApiClient(unittest.IsolatedAsyncioTestCase):
    """Test cases for the Confluence API client."""
    
    def setUp(self):
        """Set up test client."""
        self.api_client = ConfluenceApiClient(
            base_url="https://test-confluence.atlassian.net",
            api_key="test-api-key",
            user_email="test@example.com"
        )
    
    async def asyncTearDown(self):
        """Clean up after tests."""
        await self.api_client.close()
    
    async def test_api_client_initialization(self):
        """Test the API client initialization."""
        self.assertEqual(self.api_client.base_url, "https://test-confluence.atlassian.net")
        self.assertEqual(self.api_client.api_key, "test-api-key")
        self.assertEqual(self.api_client.user_email, "test@example.com")
        self.assertEqual(self.api_client.api_url, "https://test-confluence.atlassian.net/wiki/rest/api")
    
    async def test_get_successful_request(self):
        """Test a successful GET request."""
        test_response = {"results": [{"id": "123", "name": "Test Space"}]}
        
        # Mock the client's get method
        self.api_client.client.get = AsyncMock(return_value=httpx.Response(
            status_code=200,
            content=json.dumps(test_response).encode(),
            request=httpx.Request("GET", "https://test-confluence.atlassian.net/wiki/rest/api/spaces")
        ))
        
        response = await self.api_client.get("spaces", {"limit": 10})
        self.assertEqual(response, test_response)
        
        # Verify the call
        self.api_client.client.get.assert_called_once()
    
    async def test_get_error_response(self):
        """Test handling of an error response."""
        error_response = {"message": "Not found", "details": "The requested resource was not found"}
        
        # Mock the client's get method
        self.api_client.client.get = AsyncMock(return_value=httpx.Response(
            status_code=404,
            content=json.dumps(error_response).encode(),
            request=httpx.Request("GET", "https://test-confluence.atlassian.net/wiki/rest/api/spaces/INVALID")
        ))
        
        with self.assertRaises(ConfluenceError) as exc_info:
            await self.api_client.get("spaces/INVALID")
        
        self.assertEqual(exc_info.exception.status_code, 404)
        self.assertEqual(exc_info.exception.message, "Not found")
        self.assertEqual(exc_info.exception.detailed_message, "The requested resource was not found")
    
    async def test_post_successful_request(self):
        """Test a successful POST request."""
        request_data = {"title": "New Page", "spaceId": "123", "status": "current"}
        test_response = {"id": "456", "title": "New Page", "spaceId": "123"}
        
        # Mock the client's post method
        self.api_client.client.post = AsyncMock(return_value=httpx.Response(
            status_code=200,
            content=json.dumps(test_response).encode(),
            request=httpx.Request("POST", "https://test-confluence.atlassian.net/wiki/rest/api/pages")
        ))
        
        response = await self.api_client.post("content", request_data)
        self.assertEqual(response, test_response)
        
        # Verify the call
        self.api_client.client.post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
