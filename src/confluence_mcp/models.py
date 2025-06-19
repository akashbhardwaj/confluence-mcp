"""Models for the Confluence MCP server."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel


class ConfluenceError(Exception):
    """Confluence API error exception."""

    def __init__(self, message: str, status_code: int, detailed_message: Optional[str] = None):
        """Initialize the error.

        Args:
            message: Error message
            status_code: HTTP status code
            detailed_message: Detailed error information
        """
        self.message = message
        self.status_code = status_code
        self.detailed_message = detailed_message
        super().__init__(self.__str__())

    def __str__(self) -> str:
        """String representation of the error."""
        if self.detailed_message:
            return f"{self.message} (Status: {self.status_code}) - {self.detailed_message}"
        return f"{self.message} (Status: {self.status_code})"


class MCPResponse:
    """Dynamic MCP response format."""

    def __init__(self, value: Any = None, display: Optional[str] = None):
        """Initialize the MCP response.

        Args:
            value: The data to return
            display: Human-readable display text
        """
        self.value = value
        self.display = display
