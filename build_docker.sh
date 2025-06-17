#!/bin/bash
set -e

# Build the Docker image
echo "Building Confluence MCP Docker image..."
docker build -t confluence-mcp:latest .

# Output message
echo "Docker image built successfully."
echo ""
echo "Make sure to set these environment variables in your ~/.zshrc:"
echo "export CONFLUENCE_URL=https://your-domain.atlassian.net/wiki"
echo "export CONFLUENCE_API_KEY=your-api-key"
echo "export CONFLUENCE_USER_EMAIL=your-email@example.com"
echo "export DEBUG=true  # Optional: Enable debug logging"
echo ""
echo "Then reload your shell and run the image with:"
echo "docker run -p 3846:3846 -e CONFLUENCE_URL -e CONFLUENCE_API_KEY -e CONFLUENCE_USER_EMAIL -e DEBUG confluence-mcp:latest"
