#!/usr/bin/env python3
"""Test environment variable loading."""

import os
import sys

sys.path.insert(0, "src")

from confluence_mcp.config import settings

print("=== Environment Variable Test ===")
print()

print("Direct environment variables:")
print(f"JIRA_BASE_URL: {os.getenv('JIRA_BASE_URL', 'NOT SET')}")
print(f"JIRA_API_TOKEN: {'SET' if os.getenv('JIRA_API_TOKEN') else 'NOT SET'}")
print(f"JIRA_API_USER: {os.getenv('JIRA_API_USER', 'NOT SET')}")
print(f"DEBUG: {os.getenv('DEBUG', 'NOT SET')}")

print()
print("Settings object values:")
print(f"settings.JIRA_BASE_URL: {settings.JIRA_BASE_URL}")
print(f"settings.JIRA_API_TOKEN: {'SET' if settings.JIRA_API_TOKEN else 'NOT SET'}")
print(f"settings.JIRA_API_USER: {settings.JIRA_API_USER}")
print(f"settings.DEBUG: {settings.DEBUG}")

print()
if settings.JIRA_BASE_URL:
    print("Testing API client initialization...")
    try:
        from confluence_mcp.api_client import ConfluenceApiClient

        client = ConfluenceApiClient()
        print(f"✓ API client initialized successfully")
        print(f"  Base URL: {client.base_url}")
        print(f"  API URL: {client.api_url}")
    except Exception as e:
        print(f"✗ API client initialization failed: {e}")
else:
    print("Cannot test API client - JIRA_BASE_URL not set")
