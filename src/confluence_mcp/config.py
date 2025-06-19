"""Configuration settings for the Confluence MCP server."""

from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict


class Settings(BaseSettings):
    """Configuration settings."""

    model_config = ConfigDict(extra="ignore")

    # Confluence API settings
    JIRA_BASE_URL: str = ""
    JIRA_API_TOKEN: str = ""
    JIRA_API_USER: str = ""

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 3846
    DEBUG: bool = False

    @field_validator("JIRA_BASE_URL")
    def validate_confluence_url(cls, v: str) -> str:
        """Validate and normalize the Confluence URL."""
        if not v:  # Allow empty string for testing
            return v

        v = v.rstrip("/")
        if not v.startswith(("http://", "https://")):
            raise ValueError("JIRA_BASE_URL must start with http:// or https://")
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


settings = Settings()
