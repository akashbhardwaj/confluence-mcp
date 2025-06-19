"""Tests for space-related MCP functions."""

import pytest
from unittest.mock import AsyncMock, patch

from src.confluence_mcp.functions.space import list_spaces_impl, get_space_impl


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.space.get_client")
async def test_list_spaces_no_filters(mock_get_client):
    """Test listing spaces without filters."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(
        return_value={
            "results": [
                {
                    "id": "123",
                    "key": "TEST",
                    "name": "Test Space",
                    "type": "global",
                    "status": "current",
                    "description": {"plain": {"value": "Test description"}},
                },
                {
                    "id": "456",
                    "key": "DEV",
                    "name": "Development Space",
                    "type": "global",
                    "status": "current",
                },
            ]
        }
    )

    # Call the function
    result = await list_spaces_impl()

    # Verify the result
    assert "spaces" in result
    assert len(result["spaces"]) == 2
    assert result["spaces"][0]["id"] == "123"
    assert result["spaces"][0]["key"] == "TEST"
    assert result["spaces"][1]["id"] == "456"
    assert result["spaces"][1]["key"] == "DEV"

    # Verify API call
    mock_client.get.assert_called_once_with("spaces", {"limit": 25})


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.space.get_client")
async def test_list_spaces_with_filters(mock_get_client):
    """Test listing spaces with filters."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(
        return_value={
            "results": [
                {
                    "id": "123",
                    "key": "TEST",
                    "name": "Test Space",
                    "type": "global",
                    "status": "current",
                }
            ]
        }
    )

    # Call the function with filters
    result = await list_spaces_impl(keys=["TEST"], status="current", type="global", limit=10)

    # Verify the result
    assert result is not None
    assert len(result["spaces"]) == 1
    assert result["spaces"][0]["key"] == "TEST"

    # Verify API call
    mock_client.get.assert_called_once_with(
        "spaces", {"limit": 10, "keys": "TEST", "status": "current", "type": "global"}
    )


@pytest.mark.asyncio
@patch("src.confluence_mcp.functions.space.get_client")
async def test_get_space_by_id(mock_get_client):
    """Test getting a space by ID."""
    # Setup mock response
    mock_client = mock_get_client.return_value
    mock_client.get = AsyncMock(
        return_value={
            "id": "123",
            "key": "TEST",
            "name": "Test Space",
            "type": "global",
            "status": "current",
            "description": {"plain": {"value": "Test description"}},
        }
    )

    # Call the function
    result = await get_space_impl(id="123")
    # Verify the result
    assert "space" in result
    assert result["space"]["id"] == "123"
    assert result["space"]["key"] == "TEST"
    assert result["space"]["name"] == "Test Space"
    # Verify API call
    mock_client.get.assert_called_once_with("spaces/123")
