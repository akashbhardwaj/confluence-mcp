"""Configuration settings for the Confluence MCP server."""

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Configuration settings."""
    
    # Confluence API settings
    CONFLUENCE_URL: str = ""
    CONFLUENCE_API_KEY: str = ""
    CONFLUENCE_USER_EMAIL: str = ""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 3846
    DEBUG: bool = False
    
    @field_validator("CONFLUENCE_URL")
    def validate_confluence_url(cls, v: str) -> str:
        """Validate and normalize the Confluence URL."""
        if not v:  # Allow empty string for testing
            return v
            
        v = v.rstrip("/")
        if not v.startswith(("http://", "https://")):
            raise ValueError("CONFLUENCE_URL must start with http:// or https://")
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }


settings = Settings()
