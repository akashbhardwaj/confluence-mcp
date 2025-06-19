"""Tests for search-related MCP functions using unittest."""

import sys
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch
import unittest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Mock the fastmcp.v2 module
sys.modules["fastmcp.v2"] = MagicMock()
sys.modules["fastmcp.v2"].MCPFunction = MagicMock()
sys.modules["fastmcp.v2"].MCPFunction.create = lambda: lambda f: f
sys.modules["fastmcp.v2"].MCPResponse = lambda value=None, display=None: MagicMock(
    value=value, display=display
)

# Now import the functions after mocking
from src.confluence_mcp.functions.search import search_content_impl, _build_cql_query


class TestSearchFunctions(unittest.IsolatedAsyncioTestCase):
    """Tests for search-related MCP functions."""

    @patch("src.confluence_mcp.functions.search.get_client")
    async def test_search_content_basic(self, mock_get_client):
        """Test basic content search."""
        # Setup mock response
        mock_client = mock_get_client.return_value
        mock_client.get = AsyncMock(
            return_value={
                "results": [
                    {
                        "content": {
                            "id": "123",
                            "title": "Test Page",
                            "type": "page",
                            "space": {"id": "SPACE-123"},
                        },
                        "title": "Test Page",
                        "excerpt": "This is a <b>test</b> page...",
                    },
                    {
                        "content": {
                            "id": "456",
                            "title": "Another Page",
                            "type": "page",
                            "space": {"id": "SPACE-123"},
                        },
                        "title": "Another Page",
                        "excerpt": "This is <b>another</b> test page...",
                    },
                ]
            }
        )

        # Call the function
        result = await search_content_impl(query="test")

        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["content"]["id"], "123")
        self.assertEqual(result["results"][1]["content"]["id"], "456")

        # Verify API call
        mock_client.get.assert_called_once_with(
            "search", {"cql": 'text ~ "test" AND status != archived', "limit": 25}
        )

    @patch("src.confluence_mcp.functions.search.get_client")
    async def test_search_content_with_filters(self, mock_get_client):
        """Test content search with filters."""
        # Setup mock response
        mock_client = mock_get_client.return_value
        mock_client.get = AsyncMock(
            return_value={
                "results": [
                    {
                        "content": {
                            "id": "123",
                            "title": "Test Page",
                            "type": "page",
                            "space": {"id": "SPACE-123"},
                        },
                        "title": "Test Page",
                        "excerpt": "This is a <b>test</b> page...",
                    }
                ]
            }
        )

        # Call the function with filters
        result = await search_content_impl(
            query="test", space_id="SPACE-123", content_type="page", limit=10
        )

        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["content"]["id"], "123")

        # Verify API call
        mock_client.get.assert_called_once_with(
            "search",
            {
                "cql": 'text ~ "test" AND space.id = SPACE-123 AND type = page AND status != archived',
                "limit": 10,
            },
        )

    def test_build_cql_query_basic(self):
        """Test basic CQL query building."""
        query = _build_cql_query("test")
        self.assertEqual(query, 'text ~ "test" AND status != archived')

    def test_build_cql_query_with_filters(self):
        """Test CQL query building with filters."""
        query = _build_cql_query(query="test", space_id="SPACE-123", content_type="page")
        self.assertEqual(
            query, 'text ~ "test" AND space.id = SPACE-123 AND type = page AND status != archived'
        )

    def test_build_cql_query_with_archived(self):
        """Test CQL query building with archived content included."""
        query = _build_cql_query(query="test", include_archived=True)
        self.assertEqual(query, 'text ~ "test"')


if __name__ == "__main__":
    unittest.main()
