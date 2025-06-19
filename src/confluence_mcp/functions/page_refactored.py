"""Page-related MCP functions."""

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
import logging

from ..api_client import get_client
from ..mcp_server import mcp

# Set up logging
logger = logging.getLogger("confluence_mcp.functions.page")


async def list_pages_impl(
    space_id: str,
    status: Optional[str] = None,
    title: Optional[str] = None,
    limit: int = 25,
    fetch_all: bool = False,
) -> Dict[str, Any]:
    """Implementation for listing pages in a Confluence space.

    Args:
        space_id: Space ID to list pages from
        status: Filter by page status ('current', 'draft', 'archived', 'trashed')
        title: Filter by page title
        limit: Maximum number of pages to return per page
        fetch_all: Whether to fetch all pages of results

    Returns:
        Dictionary with pages information
    """
    client = get_client()

    # Build query parameters
    params = {"limit": limit, "space-id": space_id}
    if status:
        params["status"] = status
    if title:
        params["title"] = title

    logger.info(f"Listing pages with params: {params}, fetch_all={fetch_all}")

    try:
        # Fetch all pages if requested
        if fetch_all:
            pages_list = await client.fetch_all_pages("content", params)
            display_message = f"Retrieved {len(pages_list)} pages from space {space_id}"
            return {"pages": pages_list, "count": len(pages_list), "message": display_message}
        else:
            # Fetch single page
            pages = await client.get("content", params)
            result_count = len(pages.get("results", []))
            total_count = pages.get("size", 0)

            display_message = f"Retrieved {result_count} pages from space {space_id}"
            if total_count > result_count:
                display_message += (
                    f" (showing {result_count} of {total_count}, use fetch_all=True to get all)"
                )

            return {
                "pages": pages.get("results", []),
                "count": result_count,
                "total": total_count,
                "message": display_message,
            }
    except Exception as e:
        logger.error(f"Error listing pages: {str(e)}")
        # Re-raise the exception to be handled by FastMCP
        raise


@mcp.tool
async def list_pages(
    space_id: str,
    status: Optional[str] = None,
    title: Optional[str] = None,
    limit: int = 25,
    fetch_all: bool = False,
) -> Dict[str, Any]:
    """List pages in a Confluence space.

    Args:
        space_id: Space ID to list pages from
        status: Filter by page status ('current', 'draft', 'archived', 'trashed')
        title: Filter by page title
        limit: Maximum number of pages to return per page
        fetch_all: Whether to fetch all pages of results

    Returns:
        List of pages
    """
    return await list_pages_impl(space_id, status, title, limit, fetch_all)


async def get_page_impl(
    id: str,
    version: Optional[int] = None,
    body_format: Optional[str] = "storage",
    expand: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Implementation for getting a page by ID.

    Args:
        id: Page ID
        version: Specific version number to retrieve (optional)
        body_format: Body format to retrieve ('storage', 'view', 'export_view', 'styled_view', 'anonymous_export_view')
        expand: Additional fields to expand in the response (e.g., 'version', 'body.view', 'ancestors')

    Returns:
        Dictionary with page details
    """
    client = get_client()

    # Build query parameters for body format and expand
    params = {}
    if body_format:
        params["body-format"] = body_format
    if expand:
        params["expand"] = ",".join(expand)

    # Build path with optional version
    path = f"content/{id}"
    if version:
        path = f"{path}/versions/{version}"

    logger.info(f"Getting page {id} (version: {version}, format: {body_format})")

    try:
        page = await client.get(path, params)
        return {"page": page, "message": f"Page {page.get('title', id)} retrieved successfully"}
    except Exception as e:
        logger.error(f"Error getting page {id}: {str(e)}")
        # Re-raise the exception to be handled by FastMCP
        raise


@mcp.tool
async def get_page(
    id: str,
    version: Optional[int] = None,
    body_format: Optional[str] = "storage",
    expand: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get a page by ID.

    Args:
        id: Page ID
        version: Specific version number to retrieve (optional)
        body_format: Body format to retrieve ('storage', 'view', 'export_view', 'styled_view', 'anonymous_export_view')
        expand: Additional fields to expand in the response (e.g., 'version', 'body.view', 'ancestors')

    Returns:
        Page details
    """
    return await get_page_impl(id, version, body_format, expand)


async def create_page_impl(
    space_id: str,
    title: str,
    body: Dict[str, Any],
    parent_id: Optional[str] = None,
    status: Optional[str] = "current",
) -> Dict[str, Any]:
    """Implementation for creating a new page in Confluence.

    Args:
        space_id: ID of the space to create page in
        title: Page title
        body: Page body content (dict with 'representation' and 'value' keys)
        parent_id: Parent page ID (optional)
        status: Page status ('current' or 'draft')

    Returns:
        Dictionary with created page details
    """
    client = get_client()

    # Build request data
    data = {"spaceId": space_id, "title": title, "body": body, "status": status}

    if parent_id:
        data["parentId"] = parent_id

    logger.info(f"Creating page '{title}' in space {space_id}")

    try:
        page = await client.post("content", data)
        return {"page": page, "message": f"Page '{title}' created successfully"}
    except Exception as e:
        logger.error(f"Error creating page '{title}': {str(e)}")
        # Re-raise the exception to be handled by FastMCP
        raise


@mcp.tool
async def create_page(
    space_id: str,
    title: str,
    body: Dict[str, Any],
    parent_id: Optional[str] = None,
    status: Optional[str] = "current",
) -> Dict[str, Any]:
    """Create a new page in Confluence.

    Args:
        space_id: ID of the space to create page in
        title: Page title
        body: Page body content (dict with 'representation' and 'value' keys)
        parent_id: Parent page ID (optional)
        status: Page status ('current' or 'draft')

    Returns:
        Created page details
    """
    return await create_page_impl(space_id, title, body, parent_id, status)


async def update_page_impl(
    id: str,
    title: Optional[str] = None,
    body: Optional[Dict[str, Any]] = None,
    version: Optional[Dict[str, Any]] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Implementation for updating an existing Confluence page.

    Args:
        id: Page ID to update
        title: New page title (optional)
        body: New page body (optional, dict with 'representation' and 'value' keys)
        version: Version information (required, dict with 'number' and 'message' keys)
        status: New page status (optional, 'current' or 'draft')

    Returns:
        Dictionary with updated page details
    """
    client = get_client()

    logger.info(f"Updating page {id}")

    # First get the current page to get the version number if not provided
    if not version:
        try:
            current_page = await client.get(f"content/{id}")
            version = {
                "number": current_page.get("version", {}).get("number", 1) + 1,
                "message": "Updated via MCP",
            }
            logger.info(f"Auto-incrementing version to {version['number']}")
        except Exception as e:
            logger.error(f"Error fetching current page version: {str(e)}")
            raise

    # Build request data with only provided fields
    data = {"id": id, "version": version}

    if title:
        data["title"] = title

    if body:
        data["body"] = body

    if status:
        data["status"] = status

    try:
        page = await client.put(f"content/{id}", data)
        return {"page": page, "message": f"Page {page.get('title', id)} updated successfully"}
    except Exception as e:
        logger.error(f"Error updating page {id}: {str(e)}")
        # Re-raise the exception to be handled by FastMCP
        raise


@mcp.tool
async def update_page(
    id: str,
    title: Optional[str] = None,
    body: Optional[Dict[str, Any]] = None,
    version: Optional[Dict[str, Any]] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing Confluence page.

    Args:
        id: Page ID to update
        title: New page title (optional)
        body: New page body (optional, dict with 'representation' and 'value' keys)
        version: Version information (required, dict with 'number' and 'message' keys)
        status: New page status (optional, 'current' or 'draft')

    Returns:
        Updated page details
    """
    return await update_page_impl(id, title, body, version, status)


async def delete_page_impl(id: str) -> Dict[str, Any]:
    """Implementation for deleting a Confluence page.

    Args:
        id: Page ID to delete

    Returns:
        Dictionary with deletion confirmation
    """
    client = get_client()

    logger.info(f"Deleting page {id}")

    try:
        await client.delete(f"content/{id}")
        return {"id": id, "deleted": True, "message": f"Page with ID {id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting page {id}: {str(e)}")
        # Re-raise the exception to be handled by FastMCP
        raise


@mcp.tool
async def delete_page(id: str) -> Dict[str, Any]:
    """Delete a Confluence page.

    Args:
        id: Page ID to delete

    Returns:
        Confirmation of deletion
    """
    return await delete_page_impl(id)
