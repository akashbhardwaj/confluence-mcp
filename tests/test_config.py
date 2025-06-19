"""Tests for the configuration module."""

import pytest
from unittest.mock import patch
import os

from src.confluence_mcp.config import Settings


@pytest.fixture
def env_vars():
    """Set up test environment variables."""
    os.environ["JIRA_BASE_URL"] = "https://test-confluence.atlassian.net"
    os.environ["JIRA_API_TOKEN"] = "test-api-key"
    os.environ["JIRA_API_USER"] = "test@example.com"
    os.environ["DEBUG"] = "true"
    os.environ["HOST"] = "localhost"
    os.environ["PORT"] = "3000"

    yield

    # Clean up
    for key in ["JIRA_BASE_URL", "JIRA_API_TOKEN", "JIRA_API_USER", "DEBUG", "HOST", "PORT"]:
        if key in os.environ:
            del os.environ[key]


def test_settings_initialization(env_vars):
    """Test that settings are correctly initialized from environment variables."""
    settings = Settings()

    assert settings.JIRA_BASE_URL == "https://test-confluence.atlassian.net"
    assert settings.JIRA_API_TOKEN == "test-api-key"
    assert settings.JIRA_API_USER == "test@example.com"
    assert settings.DEBUG is True
    assert settings.HOST == "localhost"
    assert settings.PORT == 3000


def test_confluence_url_validator():
    """Test the URL validator."""
    # URL with trailing slash
    with patch.dict(
        os.environ,
        {
            "JIRA_BASE_URL": "https://test-confluence.atlassian.net/",
            "JIRA_API_TOKEN": "test-api-key",
            "JIRA_API_USER": "test@example.com",
        },
    ):
        settings = Settings()
        assert settings.JIRA_BASE_URL == "https://test-confluence.atlassian.net"

    # URL without scheme
    with pytest.raises(ValueError, match="JIRA_BASE_URL must start with http:// or https://"):
        with patch.dict(
            os.environ,
            {
                "JIRA_BASE_URL": "test-confluence.atlassian.net",
                "JIRA_API_TOKEN": "test-api-key",
                "JIRA_API_USER": "test@example.com",
            },
        ):
            Settings()
