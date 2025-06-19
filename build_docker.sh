#!/bin/bash
set -e

# Build the Docker image
echo "Building Confluence MCP Docker image..."
docker build -t confluence-mcp:latest .

# Output message
echo "Docker image built successfully."
echo ""
echo "Make sure to set these environment variables in your ~/.zshrc:"
echo "export JIRA_BASE_URL=https://your-domain.atlassian.net/wiki"
echo "export JIRA_API_TOKEN=your-api-key"
echo "export JIRA_API_USER=your-email@example.com"
echo "export DEBUG=true  # Optional: Enable debug logging"
echo ""
echo "Then reload your shell and run the image with:"
echo "docker run -p 3846:3846 -e JIRA_BASE_URL -e JIRA_API_TOKEN -e JIRA_API_USER -e DEBUG confluence-mcp:latest"
