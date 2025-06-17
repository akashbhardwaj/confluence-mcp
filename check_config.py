#!/usr/bin/env python3
"""Check Confluence MCP configuration."""

import os
import sys

def check_config():
    """Check that all required environment variables are set."""
    required_vars = [
        "CONFLUENCE_URL",
        "CONFLUENCE_API_KEY", 
        "CONFLUENCE_USER_EMAIL"
    ]
    
    print("=== Confluence MCP Configuration Check ===")
    print()
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == "CONFLUENCE_API_KEY":
                # Mask the API key for security
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "*" * len(value)
                print(f"✓ {var}: {masked_value}")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: NOT SET")
            all_set = False
    
    # Check optional DEBUG setting
    debug = os.getenv("DEBUG", "False")
    print(f"  DEBUG: {debug}")
    
    print()
    
    if all_set:
        print("✓ All required environment variables are set!")
        
        # Test URL format
        confluence_url = os.getenv("CONFLUENCE_URL")
        if not confluence_url.startswith(("http://", "https://")):
            print(f"⚠️  Warning: CONFLUENCE_URL should start with http:// or https://")
            print(f"   Current value: {confluence_url}")
            all_set = False
        
        if confluence_url.endswith("/"):
            print(f"⚠️  Note: CONFLUENCE_URL should not end with '/' (it will be stripped)")
            
    else:
        print("✗ Missing required environment variables!")
        print()
        print("To fix this, add these lines to your ~/.zshrc or ~/.bashrc:")
        print()
        for var in required_vars:
            if not os.getenv(var):
                if var == "CONFLUENCE_URL":
                    print(f"export {var}=https://your-domain.atlassian.net/wiki")
                elif var == "CONFLUENCE_API_KEY":
                    print(f"export {var}=your-api-key")
                elif var == "CONFLUENCE_USER_EMAIL":
                    print(f"export {var}=your-email@example.com")
        
        print()
        print("Then run: source ~/.zshrc")
    
    return all_set

if __name__ == "__main__":
    success = check_config()
    sys.exit(0 if success else 1)
