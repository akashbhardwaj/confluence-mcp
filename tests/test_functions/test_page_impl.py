"""Tests for page-related MCP implementation functions."""

import pytest
from unittest.mock import AsyncMock, patch

from src.confluence_mcp.functions.page import (
    list_pages_impl,
    get_page_impl,
    create_page_impl,
    update_page_impl,
    delete_page_impl,
)


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.page.get_client")
async def test_list_pages_no_filters(mock_get_client):
    """Test listing pages without filters."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(
        return_value={
            "results": [
                {"id": "123", "title": "Test Page", "spaceId": "SPACE-123", "status": "current"},
                {"id": "456", "title": "Another Page", "spaceId": "SPACE-123", "status": "current"},
            ],
            "size": 2,
        }
    )

    # Call the implementation function directly
    result = await list_pages_impl(space_id="SPACE-123")

    # Verify the result
    assert "pages" in result
    assert len(result["pages"]) == 2
    assert result["pages"][0]["id"] == "123"
    assert result["pages"][0]["title"] == "Test Page"
    assert result["pages"][1]["id"] == "456"
    assert result["pages"][1]["title"] == "Another Page"
    assert result["count"] == 2
    assert result["total"] == 2
    assert "message" in result

    # Verify API call
    mock_client.get.assert_called_once_with("content", {"limit": 25, "space-id": "SPACE-123"})


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.page.get_client")
async def test_list_pages_with_filters(mock_get_client):
    """Test listing pages with filters."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(
        return_value={
            "results": [
                {"id": "123", "title": "Test Page", "spaceId": "SPACE-123", "status": "current"}
            ],
            "size": 1,
        }
    )

    # Call the implementation function with filters
    result = await list_pages_impl(space_id="SPACE-123", status="current", title="Test", limit=10)

    # Verify the result
    assert "pages" in result
    assert len(result["pages"]) == 1
    assert result["pages"][0]["title"] == "Test Page"
    assert result["count"] == 1
    assert result["total"] == 1
    assert "message" in result

    # Verify API call
    mock_client.get.assert_called_once_with(
        "content", {"limit": 10, "space-id": "SPACE-123", "status": "current", "title": "Test"}
    )


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.page.get_client")
async def test_list_pages_fetch_all(mock_get_client):
    """Test listing pages with fetch_all flag."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.fetch_all_pages = AsyncMock(
        return_value=[
            {"id": "123", "title": "Test Page", "spaceId": "SPACE-123"},
            {"id": "456", "title": "Another Page", "spaceId": "SPACE-123"},
        ]
    )

    # Call the implementation function with fetch_all
    result = await list_pages_impl(space_id="SPACE-123", fetch_all=True)

    # Verify the result
    assert "pages" in result
    assert len(result["pages"]) == 2
    assert result["count"] == 2
    assert "message" in result

    # Verify API call
    mock_client.fetch_all_pages.assert_called_once_with(
        "content", {"limit": 25, "space-id": "SPACE-123"}
    )


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.page.get_client")
async def test_get_page(mock_get_client):
    """Test getting a page by ID."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(
        return_value={
            "id": "123",
            "title": "Test Page",
            "spaceId": "SPACE-123",
            "status": "current",
            "body": {"storage": {"value": "<p>Test content</p>", "representation": "storage"}},
        }
    )

    # Call the implementation function
    result = await get_page_impl(id="123")

    # Verify the result
    assert "page" in result
    assert result["page"]["id"] == "123"
    assert result["page"]["title"] == "Test Page"
    assert result["page"]["body"]["storage"]["value"] == "<p>Test content</p>"
    assert "message" in result

    # Verify API call
    mock_client.get.assert_called_once_with("content/123", {"body-format": "storage"})


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.page.get_client")
async def test_create_page(mock_get_client):
    """Test creating a new page."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.post = AsyncMock(
        return_value={"id": "123", "title": "New Page", "spaceId": "SPACE-123", "status": "current"}
    )

    # Call the implementation function
    body = {"representation": "storage", "value": "<p>New page content</p>"}
    result = await create_page_impl(space_id="SPACE-123", title="New Page", body=body)

    # Verify the result
    assert "page" in result
    assert result["page"]["id"] == "123"
    assert result["page"]["title"] == "New Page"
    assert "message" in result

    # Verify API call
    mock_client.post.assert_called_once_with(
        "content", {"spaceId": "SPACE-123", "title": "New Page", "body": body, "status": "current"}
    )


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.page.get_client")
async def test_update_page_with_existing_version(mock_get_client):
    """Test updating a page with provided version."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.put = AsyncMock(
        return_value={"id": "123", "title": "Updated Page", "version": {"number": 5}}
    )

    # Call the implementation function with explicit version
    body = {"representation": "storage", "value": "<p>Updated content</p>"}
    version = {"number": 5, "message": "Manual update"}

    result = await update_page_impl(id="123", title="Updated Page", body=body, version=version)

    # Verify the result
    assert "page" in result
    assert result["page"]["id"] == "123"
    assert result["page"]["title"] == "Updated Page"
    assert "message" in result

    # Verify API call (should not call get since version was provided)
    mock_client.get.assert_not_called()
    mock_client.put.assert_called_once_with(
        "content/123", {"id": "123", "title": "Updated Page", "body": body, "version": version}
    )


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.page.get_client")
async def test_update_page_auto_version(mock_get_client):
    """Test updating a page with auto-incremented version."""
    # Setup mock responses
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(
        return_value={"id": "123", "title": "Test Page", "version": {"number": 1}}
    )
    mock_client.put = AsyncMock(
        return_value={"id": "123", "title": "Updated Page", "version": {"number": 2}}
    )

    # Call the implementation function without version
    result = await update_page_impl(id="123", title="Updated Page")

    # Verify the result
    assert "page" in result
    assert result["page"]["id"] == "123"
    assert result["page"]["title"] == "Updated Page"
    assert "message" in result

    # Verify API calls
    mock_client.get.assert_called_once_with("content/123")
    mock_client.put.assert_called_once_with(
        "content/123",
        {
            "id": "123",
            "title": "Updated Page",
            "version": {"number": 2, "message": "Updated via MCP"},
        },
    )


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.page.get_client")
async def test_delete_page(mock_get_client):
    """Test deleting a page."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.delete = AsyncMock(return_value={})

    # Call the implementation function
    result = await delete_page_impl(id="123")

    # Verify the result
    assert "id" in result
    assert result["id"] == "123"
    assert "deleted" in result
    assert result["deleted"] is True
    assert "message" in result

    # Verify API call
    mock_client.delete.assert_called_once_with("content/123")
