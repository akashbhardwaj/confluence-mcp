# Confluence MCP Server

A Model Context Protocol (MCP) server for Confluence that allows AI assistants to interact with Confluence data.

## Features

- **Dynamic Data Handling**: Uses JSON dictionaries for all API interactions with Confluence
- **Confluence v1 REST API**: Uses the stable v1 REST API endpoints (`/wiki/rest/api`)
- Access Confluence spaces, pages, and other content
- Search Confluence content
- Create and update pages
- Authentication using Confluence API tokens
- Docker support for easy deployment

## Prerequisites

- Python 3.10+
- UV for dependency management
- Confluence Cloud instance
- Confluence API token

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
  - **Important**: Do not include `/wiki` at the end if your URL already contains it
- `CONFLUENCE_API_KEY`: Your Confluence API token
- `CONFLUENCE_USER_EMAIL`: Email address associated with the API token
- `DEBUG`: (Optional) Set to `true` to enable debug logging

**Note**: This server uses Confluence v1 REST API endpoints (`/wiki/rest/api/content/`) for all operations.

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

## Available MCP Functions

### Spaces

- `list_spaces`: List all spaces or filter by keys, status, or type
- `get_space`: Get details of a specific space by ID

### Pages

- `list_pages`: List pages in a space
- `get_page`: Get a page by ID
- `create_page`: Create a new page
- `update_page`: Update an existing page
- `delete_page`: Delete a page

### Search

- `search_content`: Search for content in Confluence

## Dynamic Approach

This MCP server uses a dynamic approach with dictionaries for all data handling:

- No static Pydantic models for Confluence API entities
- JSON dictionaries are used for request and response data
- Direct mapping to Confluence API structure
- Flexible handling of API changes without model updates

Example of creating a page with the dynamic approach:

```python
# Request as a dictionary
page_data = {
    "spaceId": "123",
    "title": "New Page",
    "body": {
        "representation": "storage",
        "value": "<p>Hello, world!</p>"
    },
    "status": "current"
}

# API client handles the request dynamically using v1 endpoints
response = await api_client.post("content", page_data)

# Response is also a dictionary
page_id = response["id"]
```

## Development

This project follows Test-Driven Development practices. To run tests:

```bash
# Run all tests
pytest

# Run function tests only
pytest tests/test_functions/ -v

# Run with coverage
pytest --cov=src
```

### Project Structure

```
src/confluence_mcp/
├── functions/          # MCP function implementations
│   ├── page.py        # Page-related functions
│   ├── search.py      # Search-related functions
│   └── space.py       # Space-related functions
├── api_client.py      # Confluence v1 REST API client
├── config.py          # Configuration management
├── main.py           # MCP server entry point
└── models.py         # Error models and utilities
```

## Docker Deployment

You can run the Confluence MCP server in a Docker container for easier deployment and isolation.

### Prerequisites for Docker

- Docker installed on your system
- Confluence API credentials available

### Running with Docker

1. Set your environment variables in your shell configuration (e.g., `~/.zshrc` or `~/.bashrc`):

```bash
# Add these lines to your ~/.zshrc or ~/.bashrc
export CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
export CONFLUENCE_API_KEY=your-api-key
export CONFLUENCE_USER_EMAIL=your-email@example.com

# Optional: Enable debug logging
export DEBUG=true
```

2. Reload your shell configuration:

```bash
source ~/.zshrc  # or source ~/.bashrc
```

3. Build the Docker image using the provided script:

```bash
chmod +x build_docker.sh
./build_docker.sh
```

4. Run the container:

```bash
docker run -d \
  --name confluence-mcp \
  -e CONFLUENCE_URL \
  -e CONFLUENCE_API_KEY \
  -e CONFLUENCE_USER_EMAIL \
  -e DEBUG \
  --restart unless-stopped \
  confluence-mcp:latest
```

**Note**: This is an MCP (Model Context Protocol) server that communicates via stdin/stdout. It's designed to be used as a subprocess by MCP clients, not as a standalone HTTP service.

### Docker Container Management

- View logs: `docker logs -f confluence-mcp`
- Stop the container: `docker stop confluence-mcp`
- Start the container again: `docker start confluence-mcp`
- Remove the container: `docker rm confluence-mcp`
