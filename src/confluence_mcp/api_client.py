"""Confluence API client."""

import httpx
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps

from .config import settings
from .models import ConfluenceError

# Set up logging
logger = logging.getLogger("confluence_mcp.api_client")


def get_client() -> 'ConfluenceApiClient':
    """Get a configured API client instance.
    
    Returns:
        ConfluenceApiClient: A new client instance
    """
    return ConfluenceApiClient(
        base_url=settings.CONFLUENCE_URL,
        api_key=settings.CONFLUENCE_API_KEY,
        user_email=settings.CONFLUENCE_USER_EMAIL
    )


def retry_on_connection_error(max_retries: int = 3, retry_delay: float = 1.0):
    """Retry decorator for connection errors.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except httpx.RequestError as e:
                    retries += 1
                    if retries > max_retries:
                        # If we've exhausted our retries, raise the error
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    # Log the retry attempt
                    logger.warning(f"Connection error, retrying ({retries}/{max_retries}): {str(e)}")
                    
                    # Wait before retrying with exponential backoff
                    await asyncio.sleep(retry_delay * (2 ** (retries - 1)))
        return wrapper
    return decorator


class ConfluenceApiClient:
    """Client for interacting with the Confluence REST API."""
    
    def __init__(self, base_url: str = None, api_key: str = None, user_email: str = None, 
                 timeout: float = 30.0, limits: httpx.Limits = None):
        """Initialize the API client.
        
        Args:
            base_url: Confluence base URL (defaults to value from settings)
            api_key: Confluence API key (defaults to value from settings)
            user_email: User email for authentication (defaults to value from settings)
            timeout: Request timeout in seconds
            limits: Connection pool limits for httpx
        """
        self.base_url = base_url or settings.CONFLUENCE_URL
        self.api_key = api_key or settings.CONFLUENCE_API_KEY
        self.user_email = user_email or settings.CONFLUENCE_USER_EMAIL
        
        # Validate required configuration
        if not self.base_url:
            raise ValueError(
                "CONFLUENCE_URL is required. Please set the CONFLUENCE_URL environment variable "
                "to your Confluence instance URL (e.g., https://your-domain.atlassian.net/wiki)"
            )
        
        if not self.api_key:
            raise ValueError(
                "CONFLUENCE_API_KEY is required. Please set the CONFLUENCE_API_KEY environment variable "
                "to your Confluence API token"
            )
            
        if not self.user_email:
            raise ValueError(
                "CONFLUENCE_USER_EMAIL is required. Please set the CONFLUENCE_USER_EMAIL environment variable "
                "to your Confluence user email"
            )
        
        # Ensure base_url has proper format
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError(
                f"CONFLUENCE_URL must start with http:// or https://. Got: {self.base_url}"
            )
        
        # Remove trailing slashes and /wiki if present to avoid duplication
        self.base_url = self.base_url.rstrip("/")
        if self.base_url.endswith("/wiki"):
            self.base_url = self.base_url[:-5]  # Remove /wiki
            logger.debug(f"Removed /wiki from base URL, now: {self.base_url}")
        
        # Use Confluence Cloud REST API v1 (more stable and widely supported)
        # v2 API is newer but has different endpoint structures and may not support all operations
        self.api_url = f"{self.base_url}/wiki/rest/api"
        
        # Set up authentication headers
        self.headers = {
            "Authorization": f"Basic {self._get_basic_auth_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        # Connection limits for optimal performance
        self.limits = limits or httpx.Limits(max_connections=10, max_keepalive_connections=5)
        
        # Initialize HTTP client with timeout and connection pooling
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=timeout,
            limits=self.limits
        )
        
        logger.info(f"Initialized Confluence API client for {self.base_url}")
        logger.debug(f"API URL: {self.api_url}")
        logger.debug(f"User email: {self.user_email}")
        logger.debug(f"API key configured: {'Yes' if self.api_key else 'No'}")
    
    def _get_basic_auth_token(self) -> str:
        """Generate Basic Auth token from email and API key.
        
        Returns:
            Base64 encoded auth token
        """
        import base64
        auth_str = f"{self.user_email}:{self.api_key}"
        return base64.b64encode(auth_str.encode()).decode()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.debug("Closed HTTP client")
    
    @retry_on_connection_error()
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the Confluence API.
        
        Args:
            path: API endpoint path
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            ConfluenceError: If the API returns an error
        """
        url = f"{self.api_url}/{path.lstrip('/')}"
        logger.debug(f"GET {url} with params: {params}")
        
        try:
            response = await self.client.get(url, params=params)
            return self._process_response(response)
        except httpx.RequestError as e:
            logger.error(f"Network error during GET request: {str(e)}")
            raise ConfluenceError(
                message=f"Network error during GET request: {str(e)}",
                status_code=0,
                detailed_message=f"URL: {url}"
            )
    
    @retry_on_connection_error()
    async def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the Confluence API.
        
        Args:
            path: API endpoint path
            data: Request payload
            
        Returns:
            Response data as dictionary
            
        Raises:
            ConfluenceError: If the API returns an error
        """
        url = f"{self.api_url}/{path.lstrip('/')}"
        logger.debug(f"POST {url} with data: {data}")
        
        try:
            response = await self.client.post(url, json=data)
            return self._process_response(response)
        except httpx.RequestError as e:
            logger.error(f"Network error during POST request: {str(e)}")
            raise ConfluenceError(
                message=f"Network error during POST request: {str(e)}",
                status_code=0,
                detailed_message=f"URL: {url}"
            )
    
    @retry_on_connection_error()
    async def put(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a PUT request to the Confluence API.
        
        Args:
            path: API endpoint path
            data: Request payload
            
        Returns:
            Response data as dictionary
            
        Raises:
            ConfluenceError: If the API returns an error
        """
        url = f"{self.api_url}/{path.lstrip('/')}"
        logger.debug(f"PUT {url} with data: {data}")
        
        try:
            response = await self.client.put(url, json=data)
            return self._process_response(response)
        except httpx.RequestError as e:
            logger.error(f"Network error during PUT request: {str(e)}")
            raise ConfluenceError(
                message=f"Network error during PUT request: {str(e)}",
                status_code=0,
                detailed_message=f"URL: {url}"
            )
    
    @retry_on_connection_error()
    async def delete(self, path: str) -> Dict[str, Any]:
        """Make a DELETE request to the Confluence API.
        
        Args:
            path: API endpoint path
            
        Returns:
            Response data as dictionary
            
        Raises:
            ConfluenceError: If the API returns an error
        """
        url = f"{self.api_url}/{path.lstrip('/')}"
        logger.debug(f"DELETE {url}")
        
        try:
            response = await self.client.delete(url)
            return self._process_response(response)
        except httpx.RequestError as e:
            logger.error(f"Network error during DELETE request: {str(e)}")
            raise ConfluenceError(
                message=f"Network error during DELETE request: {str(e)}",
                status_code=0,
                detailed_message=f"URL: {url}"
            )
    
    def _process_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Process the API response.
        
        Args:
            response: HTTP response object
            
        Returns:
            Response data as dictionary
            
        Raises:
            ConfluenceError: If the API returns an error
        """
        if response.status_code >= 400:
            try:
                error_data = response.json() if response.content else {"message": "Unknown error"}
            except Exception:
                error_data = {"message": "Failed to parse error response"}
            
            error_message = error_data.get("message", "API request failed")
            detailed_message = error_data.get("details", None)
            
            # Log the error for debugging
            logger.error(f"API error ({response.status_code}): {error_message} - {detailed_message}")
            
            # Use the API-provided message for specific error handling in tests
            # but provide more user-friendly defaults if needed
            if not error_message:
                # Custom error messages for common status codes
                if response.status_code == 401:
                    error_message = "Authentication failed. Please check your API key and credentials."
                elif response.status_code == 403:
                    error_message = "Permission denied. You don't have access to this resource."
                elif response.status_code == 404:
                    error_message = "Resource not found. Please check the ID or path."
                elif response.status_code == 429:
                    error_message = "Rate limit exceeded. Please wait before making more requests."
                else:
                    error_message = "API request failed"
            
            raise ConfluenceError(
                message=error_message,
                status_code=response.status_code,
                detailed_message=detailed_message
            )
        
        if response.content:
            try:
                return response.json()
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                raise ConfluenceError(
                    message=f"Failed to parse JSON response: {str(e)}",
                    status_code=response.status_code,
                    detailed_message=f"Response content: {response.content[:100]}..."
                )
        return {}
    
    async def fetch_all_pages(self, path: str, params: Optional[Dict[str, Any]] = None, 
                             max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch all pages of results for paginated endpoints.
        
        Args:
            path: API endpoint path
            params: Query parameters
            max_pages: Maximum number of pages to fetch (None for all)
            
        Returns:
            List of all results combined
        """
        if params is None:
            params = {}
        
        # Initialize result list and pagination variables
        all_results = []
        page_num = 1
        
        # Set initial parameters
        params["start"] = params.get("start", 0)
        params["limit"] = params.get("limit", 25)
        
        while True:
            # Make request for current page
            response = await self.get(path, params)
            
            # Extract results and add to collection
            results = response.get("results", [])
            all_results.extend(results)
            
            # Check if we've reached the end of pagination
            if not response.get("_links", {}).get("next") or len(results) < params["limit"]:
                break
            
            # Check if we've reached max_pages
            if max_pages and page_num >= max_pages:
                logger.info(f"Reached maximum page limit ({max_pages})")
                break
            
            # Update start parameter for next page
            params["start"] += params["limit"]
            page_num += 1
            
            # Log pagination progress
            logger.debug(f"Fetching page {page_num} for {path}")
        
        logger.info(f"Fetched {len(all_results)} results from {page_num} pages")
        return all_results
