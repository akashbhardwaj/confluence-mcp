"""Space-related MCP functions."""

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
import logging

from ..api_client import get_client
from ..mcp_server import mcp

# Set up logging
logger = logging.getLogger("confluence_mcp.functions.space")


# Implementation functions (for direct testing)
async def list_spaces_impl(
    keys: Optional[List[str]] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 25,
    fetch_all: bool = False,
) -> Dict[str, Any]:
    """List spaces in Confluence.

    Args:
        keys: Filter by space keys
        status: Filter by space status ('current', 'archived')
        type: Filter by space type ('global', 'personal')
        limit: Maximum number of spaces to return per page
        fetch_all: Whether to fetch all pages of results

    Returns:
        List of spaces
    """
    client = get_client()

    # Build query parameters
    params = {"limit": limit}
    if keys:
        params["keys"] = ",".join(keys)
    if status:
        params["status"] = status
    if type:
        params["type"] = type

    logger.info(f"Listing spaces with params: {params}, fetch_all={fetch_all}")

    try:
        # Fetch all pages if requested
        if fetch_all:
            spaces_list = await client.fetch_all_pages("spaces", params)
            display_message = f"Retrieved {len(spaces_list)} spaces"
            return {"spaces": spaces_list, "count": len(spaces_list), "message": display_message}
        else:
            # Fetch single page
            spaces = await client.get("spaces", params)
            result_count = len(spaces.get("results", []))
            total_count = spaces.get("size", 0)

            display_message = f"Retrieved {result_count} spaces"
            if total_count > result_count:
                display_message += (
                    f" (showing {result_count} of {total_count}, use fetch_all=True to get all)"
                )

            return {
                "spaces": spaces.get("results", []),
                "count": result_count,
                "total": total_count,
                "message": display_message,
            }
    except Exception as e:
        logger.error(f"Error listing spaces: {str(e)}")
        # Re-raise the exception to be handled by FastMCP
        raise


async def get_space_impl(id: str) -> Dict[str, Any]:
    """Get a space by ID.

    Args:
        id: Space ID

    Returns:
        Space details
    """
    client = get_client()
    logger.info(f"Getting space with ID: {id}")

    try:
        space = await client.get(f"spaces/{id}")
        return {"space": space, "message": f"Space {space.get('name', id)} retrieved successfully"}
    except Exception as e:
        logger.error(f"Error getting space {id}: {str(e)}")
        # Re-raise the exception to be handled by FastMCP
        raise


# MCP tool functions (decorated for MCP server)
@mcp.tool
async def list_spaces(
    keys: Optional[List[str]] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 25,
    fetch_all: bool = False,
) -> Dict[str, Any]:
    """List spaces in Confluence."""
    return await list_spaces_impl(keys, status, type, limit, fetch_all)


@mcp.tool
async def get_space(id: str) -> Dict[str, Any]:
    """Get a space by ID."""
    return await get_space_impl(id)
