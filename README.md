# Confluence MCP Server

A Model Context Protocol (MCP) server for Confluence that allows AI assistants to interact with Confluence data.

## Quick Start with Docker

Get started quickly using the pre-built Docker image:

```bash
docker run -d \
  --name confluence-mcp \
  -e CONFLUENCE_URL=https://your-domain.atlassian.net/wiki \
  -e CONFLUENCE_API_KEY=your-api-key \
  -e CONFLUENCE_USER_EMAIL=your-email@example.com \
  --restart unless-stopped \
  ghcr.io/akashbhardwaj/confluence-mcp:latest
```

Replace the environment variables with your actual Confluence credentials. See the [Docker Deployment](#docker-deployment) section for more details.

## Features

- Access Confluence spaces, pages, and content
- Search Confluence content
- Create, update, and delete pages
- Authentication using Confluence API tokens
- Docker support for easy deployment

## Prerequisites

- Confluence Cloud instance
- Confluence API token

For local development:
- Python 3.10+
- UV for dependency management

## Setup

1. Clone this repository
2. Install dependencies with UV:
   ```bash
   uv venv
   uv pip install -e .
   ```
3. Set up your environment variables in your shell configuration (e.g., `~/.zshrc` or `~/.bashrc`):
   ```bash
   export CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
   export CONFLUENCE_API_KEY=your-api-key
   export CONFLUENCE_USER_EMAIL=your-email@example.com
   export DEBUG=false  # Optional: set to true for debug logging
   ```
4. Reload your shell configuration:
   ```bash
   source ~/.zshrc  # or source ~/.bashrc
   ```
5. Run the server:
   ```bash
   python -m src.confluence_mcp.main
   ```

## Configuration

The server requires the following environment variables:

- `CONFLUENCE_URL`: Your Confluence Cloud URL (e.g., `https://your-domain.atlassian.net/wiki`)
- `CONFLUENCE_API_KEY`: Your Confluence API token
- `CONFLUENCE_USER_EMAIL`: Email address associated with the API token
- `DEBUG`: (Optional) Set to `true` to enable debug logging

## Usage

Once the server is running, you can configure your VS Code settings to use it:

```json
"mcp": {
    "servers": {
        "Confluence": {
            "url": "http://localhost:3846/sse"
        }
    }
}
```

## Available Functions

- **Spaces**: List spaces, get space details
- **Pages**: List, get, create, update, and delete pages
- **Search**: Search for content across Confluence

## Development

To run tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

## Docker Deployment

Pre-built Docker images are available at `ghcr.io/akashbhardwaj/confluence-mcp`.

### Using Pre-built Image (Recommended)

```bash
docker run -d \
  --name confluence-mcp \
  -e CONFLUENCE_URL=https://your-domain.atlassian.net/wiki \
  -e CONFLUENCE_API_KEY=your-api-key \
  -e CONFLUENCE_USER_EMAIL=your-email@example.com \
  --restart unless-stopped \
  ghcr.io/akashbhardwaj/confluence-mcp:latest
```

### Building Locally

```bash
chmod +x build_docker.sh
./build_docker.sh

docker run -d \
  --name confluence-mcp \
  -e CONFLUENCE_URL=https://your-domain.atlassian.net/wiki \
  -e CONFLUENCE_API_KEY=your-api-key \
  -e CONFLUENCE_USER_EMAIL=your-email@example.com \
  --restart unless-stopped \
  confluence-mcp:latest
```
