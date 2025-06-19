"""Tests for space-related MCP functions."""

import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock
import pytest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Now import the implementation functions directly for testing
from src.confluence_mcp.functions.space import (
    list_spaces_impl as list_spaces,
    get_space_impl as get_space,
)

# Using unittest instead of pytest due to import issues
import unittest


class TestSpaceFunctions(unittest.IsolatedAsyncioTestCase):
    """Tests for space-related MCP functions."""

    @patch("src.confluence_mcp.functions.space.get_client")
    async def test_list_spaces_no_filters(self, mock_get_client):
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
        result = await list_spaces()

        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(len(result["spaces"]), 2)
        self.assertEqual(result["spaces"][0]["id"], "123")
        self.assertEqual(result["spaces"][0]["key"], "TEST")
        self.assertEqual(result["spaces"][1]["id"], "456")
        self.assertEqual(result["spaces"][1]["key"], "DEV")

        # Verify API call
        mock_client.get.assert_called_once_with("spaces", {"limit": 25})

    @patch("src.confluence_mcp.functions.space.get_client")
    async def test_list_spaces_with_filters(self, mock_get_client):
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
        result = await list_spaces(keys=["TEST"], status="current", type="global", limit=10)

        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["key"], "TEST")

        # Verify API call
        mock_client.get.assert_called_once_with(
            "spaces", {"limit": 10, "keys": "TEST", "status": "current", "type": "global"}
        )

    @patch("src.confluence_mcp.functions.space.get_client")
    async def test_get_space_by_id(self, mock_get_client):
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
        result = await get_space(id="123")

        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result["space"]["id"], "123")
        self.assertEqual(result["space"]["key"], "TEST")
        self.assertEqual(result["space"]["name"], "Test Space")

        # Verify API call
        mock_client.get.assert_called_once_with("spaces/123")


if __name__ == "__main__":
    unittest.main()


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
    result = await list_spaces(keys=["TEST"], status="current", type="global", limit=10)

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
    result = await get_space(id="123")

    # Verify the result
    assert result is not None
    assert result["space"]["id"] == "123"
    assert result["space"]["key"] == "TEST"
    assert result["space"]["name"] == "Test Space"

    # Verify API call
    mock_client.get.assert_called_once_with("spaces/123")
