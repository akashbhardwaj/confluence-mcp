"""Tests for page-related MCP functions using unittest."""

import sys
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch
import unittest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Now import the implementation functions directly for testing
from src.confluence_mcp.functions.page import (
    list_pages_impl as list_pages,
    get_page_impl as get_page,
    create_page_impl as create_page,
    update_page_impl as update_page,
    delete_page_impl as delete_page
)


class TestPageFunctions(unittest.IsolatedAsyncioTestCase):
    """Tests for page-related MCP functions."""
    
    @patch("src.confluence_mcp.functions.page.get_client")
    async def test_list_pages_no_filters(self, mock_get_client):
        """Test listing pages without filters."""
        # Setup mock response
        mock_client = mock_get_client.return_value
        mock_client.get = AsyncMock(return_value={
            "results": [
                {
                    "id": "123",
                    "title": "Test Page",
                    "spaceId": "SPACE-123",
                    "status": "current"
                },
                {
                    "id": "456",
                    "title": "Another Page",
                    "spaceId": "SPACE-123",
                    "status": "current"
                }
            ]
        })
        
        # Call the function
        result = await list_pages(space_id="SPACE-123")
        
        # Verify the result
        self.assertIn("pages", result)
        self.assertEqual(len(result["pages"]), 2)
        self.assertEqual(result["pages"][0]["id"], "123")
        self.assertEqual(result["pages"][0]["title"], "Test Page")
        self.assertEqual(result["pages"][1]["id"], "456")
        self.assertEqual(result["pages"][1]["title"], "Another Page")
        
        # Verify API call
        mock_client.get.assert_called_once_with("content", {"limit": 25, "space-id": "SPACE-123"})
    
    @patch("src.confluence_mcp.functions.page.get_client")
    async def test_list_pages_with_filters(self, mock_get_client):
        """Test listing pages with filters."""
        # Setup mock response
        mock_client = mock_get_client.return_value
        mock_client.get = AsyncMock(return_value={
            "results": [
                {
                    "id": "123",
                    "title": "Test Page",
                    "spaceId": "SPACE-123",
                    "status": "current"
                }
            ]
        })
        
        # Call the function with filters
        result = await list_pages(
            space_id="SPACE-123",
            status="current",
            title="Test",
            limit=10
        )
        
        # Verify the result
        self.assertIn("pages", result)
        self.assertEqual(len(result["pages"]), 1)
        self.assertEqual(result["pages"][0]["title"], "Test Page")
        
        # Verify API call
        mock_client.get.assert_called_once_with("content", 
            {"limit": 10, "space-id": "SPACE-123", "status": "current", "title": "Test"}
        )
    
    @patch("src.confluence_mcp.functions.page.get_client")
    async def test_get_page(self, mock_get_client):
        """Test getting a page by ID."""
        # Setup mock response
        mock_client = mock_get_client.return_value
        mock_client.get = AsyncMock(return_value={
            "id": "123",
            "title": "Test Page",
            "spaceId": "SPACE-123",
            "status": "current",
            "body": {
                "storage": {
                    "value": "<p>Test content</p>",
                    "representation": "storage"
                }
            }
        })
        
        # Call the function
        result = await get_page(id="123")
        
        # Verify the result
        self.assertIn("page", result)
        self.assertEqual(result["page"]["id"], "123")
        self.assertEqual(result["page"]["title"], "Test Page")
        self.assertEqual(result["page"]["body"]["storage"]["value"], "<p>Test content</p>")
        
        # Verify API call
        mock_client.get.assert_called_once_with("content/123", {"body-format": "storage"})
    
    @patch("src.confluence_mcp.functions.page.get_client")
    async def test_create_page(self, mock_get_client):
        """Test creating a new page."""
        # Setup mock response
        mock_client = mock_get_client.return_value
        mock_client.post = AsyncMock(return_value={
            "id": "123",
            "title": "New Page",
            "spaceId": "SPACE-123",
            "status": "current"
        })
        
        # Call the function
        body = {
            "representation": "storage",
            "value": "<p>New page content</p>"
        }
        result = await create_page(
            space_id="SPACE-123",
            title="New Page",
            body=body
        )
        
        # Verify the result
        self.assertIn("page", result)
        self.assertEqual(result["page"]["id"], "123")
        self.assertEqual(result["page"]["title"], "New Page")
        
        # Verify API call
        mock_client.post.assert_called_once_with("content", 
            {
                "spaceId": "SPACE-123",
                "title": "New Page",
                "body": body,
                "status": "current"
            }
        )
    
    @patch("src.confluence_mcp.functions.page.get_client")
    async def test_update_page(self, mock_get_client):
        """Test updating an existing page."""
        # Setup mock responses
        mock_client = mock_get_client.return_value
        mock_client.get = AsyncMock(return_value={
            "id": "123",
            "title": "Test Page",
            "version": {"number": 1}
        })
        mock_client.put = AsyncMock(return_value={
            "id": "123",
            "title": "Updated Page",
            "version": {"number": 2}
        })
        
        # Call the function
        body = {
            "representation": "storage",
            "value": "<p>Updated content</p>"
        }
        result = await update_page(
            id="123",
            title="Updated Page",
            body=body
        )
        
        # Verify the result
        self.assertIn("page", result)
        self.assertEqual(result["page"]["id"], "123")
        self.assertEqual(result["page"]["title"], "Updated Page")
        
        # Verify API calls
        mock_client.get.assert_called_once_with("content/123")
        mock_client.put.assert_called_once_with(
            "content/123", 
            {
                "id": "123",
                "title": "Updated Page",
                "body": body,
                "version": {"number": 2, "message": "Updated via MCP"}
            }
        )
    
    @patch("src.confluence_mcp.functions.page.get_client")
    async def test_delete_page(self, mock_get_client):
        """Test deleting a page."""
        # Setup mock response
        mock_client = mock_get_client.return_value
        mock_client.delete = AsyncMock(return_value={})
        
        # Call the function
        result = await delete_page(id="123")
        
        # Verify the result
        self.assertIn("id", result)
        self.assertEqual(result["id"], "123")
        self.assertIn("deleted", result)
        self.assertTrue(result["deleted"])
        
        # Verify API call
        mock_client.delete.assert_called_once_with("content/123")


if __name__ == '__main__':
    unittest.main()
