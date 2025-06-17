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
    advanced_search
)

def run():
    """Run the MCP server."""
    logger.info("Starting Confluence MCP server")
    
    # Validate configuration before starting
    try:
        logger.debug(f"Configuration check:")
        logger.debug(f"  CONFLUENCE_URL: {settings.CONFLUENCE_URL if settings.CONFLUENCE_URL else 'NOT SET'}")
        logger.debug(f"  CONFLUENCE_API_KEY: {'SET' if settings.CONFLUENCE_API_KEY else 'NOT SET'}")
        logger.debug(f"  CONFLUENCE_USER_EMAIL: {settings.CONFLUENCE_USER_EMAIL if settings.CONFLUENCE_USER_EMAIL else 'NOT SET'}")
        logger.debug(f"  DEBUG: {settings.DEBUG}")
        
        # Also check environment variables directly
        import os
        logger.debug(f"Environment variables:")
        logger.debug(f"  CONFLUENCE_URL (env): {os.getenv('CONFLUENCE_URL', 'NOT SET')}")
        logger.debug(f"  CONFLUENCE_API_KEY (env): {'SET' if os.getenv('CONFLUENCE_API_KEY') else 'NOT SET'}")
        logger.debug(f"  CONFLUENCE_USER_EMAIL (env): {os.getenv('CONFLUENCE_USER_EMAIL', 'NOT SET')}")
        logger.debug(f"  DEBUG (env): {os.getenv('DEBUG', 'NOT SET')}")
        
        if not settings.CONFLUENCE_URL:
            logger.error("CONFLUENCE_URL environment variable is not set!")
            logger.error("Please set: export CONFLUENCE_URL=https://your-domain.atlassian.net/wiki")
            
        if not settings.CONFLUENCE_API_KEY:
            logger.error("CONFLUENCE_API_KEY environment variable is not set!")
            logger.error("Please set: export CONFLUENCE_API_KEY=your-api-key")
            
        if not settings.CONFLUENCE_USER_EMAIL:
            logger.error("CONFLUENCE_USER_EMAIL environment variable is not set!")
            logger.error("Please set: export CONFLUENCE_USER_EMAIL=your-email@example.com")
            
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
