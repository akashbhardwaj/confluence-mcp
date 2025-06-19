"""Mock FastMCP classes for testing."""

from typing import Any, Callable, Dict, Optional


class MCPFunction:
    """Mock MCPFunction decorator."""

    @staticmethod
    def create():
        """Create a mock MCPFunction decorator."""

        def decorator(func):
            return func

        return decorator


class MCPResponse:
    """Mock MCPResponse class."""

    def __init__(self, value: Any = None, display: Optional[str] = None):
        """Initialize the mock MCPResponse."""
        self.value = value
        self.display = display
