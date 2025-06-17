"""Tests for the configuration module."""

import pytest
from unittest.mock import patch
import os

from src.confluence_mcp.config import Settings


@pytest.fixture
def env_vars():
    """Set up test environment variables."""
    os.environ["CONFLUENCE_URL"] = "https://test-confluence.atlassian.net"
    os.environ["CONFLUENCE_API_KEY"] = "test-api-key"
    os.environ["CONFLUENCE_USER_EMAIL"] = "test@example.com"
    os.environ["DEBUG"] = "true"
    os.environ["HOST"] = "localhost"
    os.environ["PORT"] = "3000"
    
    yield
    
    # Clean up
    for key in ["CONFLUENCE_URL", "CONFLUENCE_API_KEY", "CONFLUENCE_USER_EMAIL", "DEBUG", "HOST", "PORT"]:
        if key in os.environ:
            del os.environ[key]


def test_settings_initialization(env_vars):
    """Test that settings are correctly initialized from environment variables."""
    settings = Settings()
    
    assert settings.CONFLUENCE_URL == "https://test-confluence.atlassian.net"
    assert settings.CONFLUENCE_API_KEY == "test-api-key"
    assert settings.CONFLUENCE_USER_EMAIL == "test@example.com"
    assert settings.DEBUG is True
    assert settings.HOST == "localhost"
    assert settings.PORT == 3000


def test_confluence_url_validator():
    """Test the URL validator."""
    # URL with trailing slash
    with patch.dict(os.environ, {
        "CONFLUENCE_URL": "https://test-confluence.atlassian.net/",
        "CONFLUENCE_API_KEY": "test-api-key",
        "CONFLUENCE_USER_EMAIL": "test@example.com"
    }):
        settings = Settings()
        assert settings.CONFLUENCE_URL == "https://test-confluence.atlassian.net"
    
    # URL without scheme
    with pytest.raises(ValueError, match="CONFLUENCE_URL must start with http:// or https://"):
        with patch.dict(os.environ, {
            "CONFLUENCE_URL": "test-confluence.atlassian.net",
            "CONFLUENCE_API_KEY": "test-api-key", 
            "CONFLUENCE_USER_EMAIL": "test@example.com"
        }):
            Settings()
