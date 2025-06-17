"""Tests for search-related MCP implementation functions."""

import pytest
from unittest.mock import AsyncMock, patch

from src.confluence_mcp.functions.search import (
    search_content_impl, advanced_search_impl, _build_cql_query
)


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.search.get_client")
async def test_search_content_basic(mock_get_client):
    """Test basic content search."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(return_value={
        "results": [
            {
                "content": {
                    "id": "123",
                    "title": "Test Page",
                    "type": "page",
                    "space": {"id": "SPACE-123"}
                },
                "title": "Test Page",
                "excerpt": "This is a <b>test</b> page..."
            },
            {
                "content": {
                    "id": "456",
                    "title": "Another Page",
                    "type": "page",
                    "space": {"id": "SPACE-123"}
                },
                "title": "Another Page",
                "excerpt": "This is <b>another</b> test page..."
            }
        ],
        "totalSize": 2
    })
    
    # Call the implementation function directly
    result = await search_content_impl(query="test")
    
    # Verify the result
    assert "results" in result
    assert len(result["results"]) == 2
    assert result["results"][0]["content"]["id"] == "123"
    assert result["results"][1]["content"]["id"] == "456"
    assert result["count"] == 2
    assert result["total"] == 2
    assert "message" in result
    
    # Verify API call
    mock_client.get.assert_called_once_with("search", {
        "cql": 'text ~ "test" AND status != archived',
        "limit": 25
    })


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.search.get_client")
async def test_search_content_with_filters(mock_get_client):
    """Test content search with filters."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(return_value={
        "results": [
            {
                "content": {
                    "id": "123",
                    "title": "Test Page",
                    "type": "page",
                    "space": {"id": "SPACE-123"}
                },
                "title": "Test Page",
                "excerpt": "This is a <b>test</b> page..."
            }
        ],
        "totalSize": 1
    })
    
    # Call the implementation function with filters
    result = await search_content_impl(
        query="test",
        space_id="SPACE-123",
        content_type="page",
        limit=10
    )
    
    # Verify the result
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["content"]["id"] == "123"
    assert result["count"] == 1
    assert result["total"] == 1
    assert "message" in result
    
    # Verify API call
    mock_client.get.assert_called_once_with("search", {
        "cql": 'text ~ "test" AND space.id = SPACE-123 AND type = page AND status != archived',
        "limit": 10
    })


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.search.get_client")
async def test_search_content_fetch_all(mock_get_client):
    """Test content search with fetch_all flag."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.fetch_all_pages = AsyncMock(return_value=[
        {
            "content": {
                "id": "123",
                "title": "Test Page",
                "type": "page"
            }
        },
        {
            "content": {
                "id": "456",
                "title": "Another Page",
                "type": "page"
            }
        }
    ])
    
    # Call the implementation function with fetch_all
    result = await search_content_impl(
        query="test",
        fetch_all=True
    )
    
    # Verify the result
    assert "results" in result
    assert len(result["results"]) == 2
    assert result["count"] == 2
    assert "message" in result
    
    # Verify API call
    mock_client.fetch_all_pages.assert_called_once_with("search", {
        "cql": 'text ~ "test" AND status != archived',
        "limit": 25
    })


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.search.get_client")
async def test_advanced_search(mock_get_client):
    """Test advanced search with custom CQL."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(return_value={
        "results": [
            {
                "content": {
                    "id": "123",
                    "title": "Test Page",
                    "type": "page"
                }
            }
        ],
        "totalSize": 1
    })
    
    # Call the implementation function
    result = await advanced_search_impl(
        cql='type = page AND text ~ "advanced"'
    )
    
    # Verify the result
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["count"] == 1
    assert result["total"] == 1
    assert "message" in result
    
    # Verify API call
    mock_client.get.assert_called_once_with("search", {
        "cql": 'type = page AND text ~ "advanced"',
        "limit": 25
    })


def test_build_cql_query_basic():
    """Test basic CQL query building."""
    query = _build_cql_query("test")
    assert query == 'text ~ "test" AND status != archived'


def test_build_cql_query_with_filters():
    """Test CQL query building with multiple filters."""
    query = _build_cql_query(
        query="test",
        space_id="SPACE-123",
        content_type="page",
        created_after="2023-01-01",
        updated_before="2023-12-31",
        creator="johndoe"
    )
    assert query == (
        'text ~ "test" AND space.id = SPACE-123 AND type = page AND '
        'status != archived AND created >= "2023-01-01" AND '
        'lastmodified <= "2023-12-31" AND creator = "johndoe"'
    )
