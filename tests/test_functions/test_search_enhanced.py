"""Tests for enhanced search features."""

import sys
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch
import unittest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock the fastmcp.v2 module
sys.modules['fastmcp.v2'] = MagicMock()
sys.modules['fastmcp.v2'].MCPFunction = MagicMock()
sys.modules['fastmcp.v2'].MCPFunction.create = lambda: lambda f: f
sys.modules['fastmcp.v2'].MCPResponse = lambda value=None, display=None: MagicMock(value=value, display=display)

# Now import the functions after mocking
from src.confluence_mcp.functions.search import search_content_impl, advanced_search_impl, _build_cql_query


class TestEnhancedSearchFunctions(unittest.IsolatedAsyncioTestCase):
    """Tests for enhanced search functions."""
    
    @patch("src.confluence_mcp.functions.search.get_client")
    async def test_search_content_with_fetch_all(self, mock_get_client):
        """Test content search with fetch_all parameter."""
        # Setup mock client
        mock_client = mock_get_client.return_value
        mock_client.fetch_all_pages = AsyncMock(return_value=[
            {
                "content": {"id": "123", "title": "Test Page"},
                "title": "Test Page",
                "excerpt": "This is a <b>test</b> page..."
            },
            {
                "content": {"id": "456", "title": "Another Test"},
                "title": "Another Test",
                "excerpt": "Another <b>test</b> result..."
            }
        ])
        
        # Call the function with fetch_all=True
        result = await search_content_impl(
            query="test",
            fetch_all=True
        )
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["content"]["id"], "123")
        self.assertEqual(result["results"][1]["content"]["id"], "456")
        
        # Verify API call
        mock_client.fetch_all_pages.assert_called_once_with(
            "search", 
            {"cql": 'text ~ "test" AND status != archived', "limit": 25}
        )
    
    @patch("src.confluence_mcp.functions.search.get_client")
    async def test_advanced_search(self, mock_get_client):
        """Test advanced search with custom CQL."""
        # Setup mock response
        mock_client = mock_get_client.return_value
        mock_client.get = AsyncMock(return_value={
            "results": [
                {
                    "content": {"id": "123", "title": "Test Page"},
                    "title": "Test Page",
                    "excerpt": "This is a <b>test</b> page..."
                }
            ],
            "totalSize": 1
        })
        
        # Custom CQL query
        custom_cql = 'text ~ "test" AND creator = "admin" AND type = page'
        
        # Call the function
        result = await advanced_search_impl(cql=custom_cql)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["content"]["id"], "123")
        
        # Verify API call
        mock_client.get.assert_called_once_with(
            "search", 
            {"cql": custom_cql, "limit": 25}
        )
    
    def test_build_cql_query_with_date_filters(self):
        """Test CQL query building with date filters."""
        query = _build_cql_query(
            query="test",
            created_after="2023-01-01",
            created_before="2023-12-31",
            updated_after="2023-06-01",
            updated_before="2023-06-30"
        )
        
        # Verify the CQL query has the correct date filters
        self.assertIn('text ~ "test"', query)
        self.assertIn('created >= "2023-01-01"', query)
        self.assertIn('created <= "2023-12-31"', query)
        self.assertIn('lastmodified >= "2023-06-01"', query)
        self.assertIn('lastmodified <= "2023-06-30"', query)
        self.assertIn('status != archived', query)
    
    def test_build_cql_query_with_user_filters(self):
        """Test CQL query building with user filters."""
        query = _build_cql_query(
            query="test",
            creator="admin",
            contributor="user123"
        )
        
        # Verify the CQL query has the correct user filters
        self.assertIn('text ~ "test"', query)
        self.assertIn('creator = "admin"', query)
        self.assertIn('contributor = "user123"', query)
        self.assertIn('status != archived', query)
    
    def test_build_cql_query_escapes_quotes(self):
        """Test that CQL query building escapes quotes in the query string."""
        query = _build_cql_query(
            query='test with "quotes"'
        )
        
        # Verify the quotes are escaped
        self.assertIn('text ~ "test with \\"quotes\\""', query)


if __name__ == '__main__':
    unittest.main()
