#!/usr/bin/env python3
"""Test environment variable loading."""

import os
import sys
sys.path.insert(0, 'src')

from confluence_mcp.config import settings

print("=== Environment Variable Test ===")
print()

print("Direct environment variables:")
print(f"CONFLUENCE_URL: {os.getenv('CONFLUENCE_URL', 'NOT SET')}")
print(f"CONFLUENCE_API_KEY: {'SET' if os.getenv('CONFLUENCE_API_KEY') else 'NOT SET'}")
print(f"CONFLUENCE_USER_EMAIL: {os.getenv('CONFLUENCE_USER_EMAIL', 'NOT SET')}")
print(f"DEBUG: {os.getenv('DEBUG', 'NOT SET')}")

print()
print("Settings object values:")
print(f"settings.CONFLUENCE_URL: {settings.CONFLUENCE_URL}")
print(f"settings.CONFLUENCE_API_KEY: {'SET' if settings.CONFLUENCE_API_KEY else 'NOT SET'}")
print(f"settings.CONFLUENCE_USER_EMAIL: {settings.CONFLUENCE_USER_EMAIL}")
print(f"settings.DEBUG: {settings.DEBUG}")

print()
if settings.CONFLUENCE_URL:
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
    print("Cannot test API client - CONFLUENCE_URL not set")
