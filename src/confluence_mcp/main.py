"""Main entry point for the Confluence MCP server."""

import logging
from .config import settings
from .mcp_server import mcp

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("confluence_mcp")

# Import functions to register them with the MCP server
from .functions import (
    list_spaces,
    get_space,
    list_pages,
    get_page,
    create_page,
    update_page,
    delete_page,
    search_content,
    advanced_search,
)


def run():
    """Run the MCP server."""
    logger.info("Starting Confluence MCP server")

    # Validate configuration before starting
    try:
        logger.debug(f"Configuration check:")
        logger.debug(
            f"  JIRA_BASE_URL: {settings.JIRA_BASE_URL if settings.JIRA_BASE_URL else 'NOT SET'}"
        )
        logger.debug(f"  JIRA_API_TOKEN: {'SET' if settings.JIRA_API_TOKEN else 'NOT SET'}")
        logger.debug(
            f"  JIRA_API_USER: {settings.JIRA_API_USER if settings.JIRA_API_USER else 'NOT SET'}"
        )
        logger.debug(f"  DEBUG: {settings.DEBUG}")

        # Also check environment variables directly
        import os

        logger.debug(f"Environment variables:")
        logger.debug(f"  JIRA_BASE_URL (env): {os.getenv('JIRA_BASE_URL', 'NOT SET')}")
        logger.debug(
            f"  JIRA_API_TOKEN (env): {'SET' if os.getenv('JIRA_API_TOKEN') else 'NOT SET'}"
        )
        logger.debug(f"  JIRA_API_USER (env): {os.getenv('JIRA_API_USER', 'NOT SET')}")
        logger.debug(f"  DEBUG (env): {os.getenv('DEBUG', 'NOT SET')}")

        if not settings.JIRA_BASE_URL:
            logger.error("JIRA_BASE_URL environment variable is not set!")
            logger.error("Please set: export JIRA_BASE_URL=https://your-domain.atlassian.net/wiki")

        if not settings.JIRA_API_TOKEN:
            logger.error("JIRA_API_TOKEN environment variable is not set!")
            logger.error("Please set: export JIRA_API_TOKEN=your-api-key")

        if not settings.JIRA_API_USER:
            logger.error("JIRA_API_USER environment variable is not set!")
            logger.error("Please set: export JIRA_API_USER=your-email@example.com")

        # Test API client initialization
        from .api_client import get_client

        client = get_client()
        logger.info("API client initialized successfully")

    except Exception as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your environment variables and try again")
        raise

    mcp.run()


if __name__ == "__main__":
    run()
