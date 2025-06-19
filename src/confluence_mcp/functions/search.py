"""Search-related MCP functions."""

from typing import Dict, Any, List, Optional
import logging

from ..api_client import get_client
from ..mcp_server import mcp

# Set up logging
logger = logging.getLogger("confluence_mcp.functions.search")


async def search_content_impl(
    query: str,
    space_id: Optional[str] = None,
    content_type: Optional[str] = None,
    limit: int = 25,
    include_archived: bool = False,
    fetch_all: bool = False,
    cql: Optional[str] = None,
) -> Dict[str, Any]:
    """Implementation for searching content in Confluence.

    Args:
        query: Search query string (ignored if cql is provided)
        space_id: Filter by space ID (optional)
        content_type: Filter by content type ('page', 'blogpost', 'comment', etc.)
        limit: Maximum number of results to return per page
        include_archived: Whether to include archived content in search
        fetch_all: Whether to fetch all pages of results
        cql: Custom CQL query string (overrides other parameters)

    Returns:
        Dictionary with search results
    """
    client = get_client()

    # Build query parameters
    params = {"limit": limit}

    # Use custom CQL if provided, otherwise build from parameters
    if cql:
        params["cql"] = cql
        logger.info(f"Searching with custom CQL: {cql}")
    else:
        params["cql"] = _build_cql_query(
            query=query,
            space_id=space_id,
            content_type=content_type,
            include_archived=include_archived,
        )
        logger.info(f"Searching with generated CQL: {params['cql']}")

    try:
        # Fetch all pages if requested
        if fetch_all:
            results_list = await client.fetch_all_pages("search", params)
            display_message = f"Found {len(results_list)} results for query '{query}'"
            return {"results": results_list, "count": len(results_list), "message": display_message}
        else:
            # Fetch single page
            results = await client.get("search", params)
            result_count = len(results.get("results", []))
            total_count = results.get("totalSize", 0)

            display_message = f"Found {result_count} results for query '{query}'"
            if total_count > result_count:
                display_message += (
                    f" (showing {result_count} of {total_count}, use fetch_all=True to get all)"
                )

            return {
                "results": results.get("results", []),
                "count": result_count,
                "total": total_count,
                "message": display_message,
            }
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        # Re-raise the exception to be handled by FastMCP
        raise


@mcp.tool
async def search_content(
    query: str,
    space_id: Optional[str] = None,
    content_type: Optional[str] = None,
    limit: int = 25,
    include_archived: bool = False,
    fetch_all: bool = False,
    cql: Optional[str] = None,
) -> Dict[str, Any]:
    """Search for content in Confluence.

    Args:
        query: Search query string (ignored if cql is provided)
        space_id: Filter by space ID (optional)
        content_type: Filter by content type ('page', 'blogpost', 'comment', etc.)
        limit: Maximum number of results to return per page
        include_archived: Whether to include archived content in search
        fetch_all: Whether to fetch all pages of results
        cql: Custom CQL query string (overrides other parameters)

    Returns:
        Search results
    """
    return await search_content_impl(
        query=query,
        space_id=space_id,
        content_type=content_type,
        limit=limit,
        include_archived=include_archived,
        fetch_all=fetch_all,
        cql=cql,
    )


async def advanced_search_impl(
    cql: str, limit: int = 25, fetch_all: bool = False
) -> Dict[str, Any]:
    """Implementation for performing an advanced search using custom CQL.

    Args:
        cql: Confluence Query Language query string
        limit: Maximum number of results to return per page
        fetch_all: Whether to fetch all pages of results

    Returns:
        Dictionary with search results
    """
    client = get_client()

    # Build query parameters
    params = {"cql": cql, "limit": limit}

    logger.info(f"Performing advanced search with CQL: {cql}")

    try:
        # Fetch all pages if requested
        if fetch_all:
            results_list = await client.fetch_all_pages("search", params)
            display_message = f"Found {len(results_list)} results for advanced search"
            return {"results": results_list, "count": len(results_list), "message": display_message}
        else:
            # Fetch single page
            results = await client.get("search", params)
            result_count = len(results.get("results", []))
            total_count = results.get("totalSize", 0)

            display_message = f"Found {result_count} results for advanced search"
            if total_count > result_count:
                display_message += (
                    f" (showing {result_count} of {total_count}, use fetch_all=True to get all)"
                )

            return {
                "results": results.get("results", []),
                "count": result_count,
                "total": total_count,
                "message": display_message,
            }
    except Exception as e:
        logger.error(f"Error in advanced search: {str(e)}")
        # Re-raise the exception to be handled by FastMCP
        raise


@mcp.tool
async def advanced_search(cql: str, limit: int = 25, fetch_all: bool = False) -> Dict[str, Any]:
    """Perform an advanced search using custom CQL.

    Args:
        cql: Confluence Query Language query string
        limit: Maximum number of results to return per page
        fetch_all: Whether to fetch all pages of results

    Returns:
        Search results
    """
    return await advanced_search_impl(cql=cql, limit=limit, fetch_all=fetch_all)


def _build_cql_query(
    query: str,
    space_id: Optional[str] = None,
    content_type: Optional[str] = None,
    include_archived: bool = False,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    creator: Optional[str] = None,
    contributor: Optional[str] = None,
) -> str:
    """Build a CQL (Confluence Query Language) query string.

    Args:
        query: Base search query
        space_id: Space ID to search in
        content_type: Content type to filter by
        include_archived: Whether to include archived content
        created_after: ISO date string (e.g. "2023-01-01")
        created_before: ISO date string
        updated_after: ISO date string
        updated_before: ISO date string
        creator: Username of content creator
        contributor: Username of content contributor

    Returns:
        CQL query string
    """
    # Start with text query (escape quotes in the query)
    query = query.replace('"', '\\"')
    cql_parts = [f'text ~ "{query}"']

    # Add space filter if provided
    if space_id:
        cql_parts.append(f"space.id = {space_id}")

    # Add content type filter if provided
    if content_type:
        cql_parts.append(f"type = {content_type}")

    # Note: Archived content filtering via 'status' field is not supported in Confluence Cloud REST API
    # The include_archived parameter is retained for potential future use or different API versions
    
    # Add date filters if provided
    if created_after:
        cql_parts.append(f'created >= "{created_after}"')
    if created_before:
        cql_parts.append(f'created <= "{created_before}"')
    if updated_after:
        cql_parts.append(f'lastmodified >= "{updated_after}"')
    if updated_before:
        cql_parts.append(f'lastmodified <= "{updated_before}"')

    # Add user filters if provided
    if creator:
        cql_parts.append(f'creator = "{creator}"')
    if contributor:
        cql_parts.append(f'contributor = "{contributor}"')

    # Join all parts with AND
    return " AND ".join(cql_parts)
