# Confluence MCP Server Development Plan

## Project Overview
We'll create a Model Context Protocol (MCP) server that integrates with Confluence's REST API. This server will allow AI assistants to interact with Confluence data through a standardized protocol.

## Technical Stack
- **FastMCP 2.x** (from [jlowin/fastmcp](https://github.com/jlowin/fastmcp)): For implementing the MCP server framework
- **UV**: For Python dependency management
- **Python**: As the primary programming language
- **FastAPI**: Underlying web framework for FastMCP
- **pytest**: For test-driven development
- **httpx**: For making HTTP requests to Confluence API
- **pydantic**: For data validation and settings management
- **Confluence API Reference**: For understanding API endpoints and responses

## Development Approach
We'll follow a Test-Driven Development (TDD) approach with unit tests:
1. Write failing unit tests
2. Implement the minimal code to pass the tests
3. Refactor while keeping tests passing
4. Use mocks for external dependencies to avoid integration testing

## Project Structure
```
confluence-mcp/
├── pyproject.toml          # Project configuration
├── README.md               # Project documentation
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
├── src/
│   └── confluence_mcp/
│       ├── __init__.py
│       ├── main.py         # FastMCP server entry point
│       ├── config.py       # Configuration management
│       ├── models.py       # Simple Pydantic models for request/response typing
│       ├── api_client.py   # Confluence API client
│       └── functions/      # MCP function implementations
│           ├── __init__.py
│           ├── space.py    # Space-related functions
│           ├── page.py     # Page-related functions
│           └── search.py   # Search-related functions
└── tests/
    ├── __init__.py
    ├── conftest.py         # Test fixtures and mocks
    ├── test_api_client.py  # Unit tests for API client
    └── test_functions/     # Unit tests for MCP functions
        ├── __init__.py
        ├── test_space.py
        ├── test_page.py
        └── test_search.py
```

## Implementation Phases

### Phase 1: Project Setup
- ✅ Initialize project structure
- ✅ Set up UV for dependency management
- ✅ Configure basic FastMCP server
- ✅ Create configuration management

### Phase 2: Confluence API Client
- ✅ Implement authentication
- ✅ Create dynamic API client using JSON dictionaries
- ✅ Add error handling

### Phase 3: Core MCP Functions
- ✅ Implement space-related functions (list, get)
- ✅ Implement page-related functions (list, get, create, update, delete)
- ✅ Implement search functions
- ✅ Run tests to verify implementation

### Phase 4: Testing and Refinement
- ✅ Expand unit test coverage
- ✅ Refine error handling
- ✅ Improve performance
- ✅ Add pagination support
- ✅ Implement retry mechanism

### Phase 5: Documentation and Deployment
- Complete README with setup and usage instructions
- Document available MCP functions
- Provide example configurations
- Transition to FastMCP 2.x from jlowin/fastmcp repository
  - Update imports and adapt to the new API
  - Ensure compatibility with existing functionality
  - Leverage enhanced features of FastMCP 2.x
- Create Docker containerization
  - Write optimized multi-stage Dockerfile
  - Add Docker setup instructions
  - Implement security best practices (non-root user)
- Test Docker deployment locally

## Core MCP Functions to Implement

1. **Space Management**
   - `list_spaces`: List available spaces
   - `get_space`: Get space details

2. **Page Management**
   - `list_pages`: List pages in a space
   - `get_page`: Get page content
   - `create_page`: Create a new page
   - `update_page`: Update page content

3. **Search**
   - `search_content`: Search for content in Confluence

## Configuration Requirements
- Confluence API URL
- API Token/Key
- User authentication details

## Testing Strategy
- Unit tests for all components with mocks for external dependencies
- Test fixtures to simulate Confluence API responses
- Focus on testing business logic rather than external integrations

## FastMCP 2.x Migration Plan

### Why Use FastMCP 2.x
FastMCP 2.x from the [jlowin/fastmcp](https://github.com/jlowin/fastmcp) repository offers several advantages:
- Comprehensive set of features beyond core MCP specification
- Improved performance and reliability
- Enhanced client capabilities
- Better authentication and security options
- Simplified deployment options

### Migration Steps
1. Update dependencies in pyproject.toml to use FastMCP 2.x
2. Refactor imports from `fastmcp.v2` to the new package structure
3. Adapt MCP server creation to use the `FastMCP` class instead of `MCP`
4. Update route registration to use new API patterns
5. Leverage enhanced context features for improved functionality
6. Update tests to reflect the new API structure
7. Test thoroughly to ensure compatibility

### Key API Changes
- Replace `MCP` with `FastMCP` for server initialization
- Use `@mcp.tool` instead of function registration methods
- Adapt to new routing patterns with `FastMCP` server
- Utilize improved Context object for enhanced capabilities
