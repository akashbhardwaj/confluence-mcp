FROM python:3.12-slim AS builder

WORKDIR /app

# Install UV for dependency management
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml .
COPY README.md .

# Copy lock file
COPY uv.lock .

# Copy source code (needed for uv sync to build the project)
COPY src/ ./src/

# Create a virtual environment and install dependencies
RUN uv sync --frozen

# Second stage: runtime
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONPATH="/app"
ENV PATH="/app/.venv/bin:$PATH"

# Create a non-root user to run the server
RUN adduser --disabled-password --gecos "" mcp-user && \
    chown -R mcp-user:mcp-user /app

# Switch to non-root user
USER mcp-user

# Create directory for possible volume mounting of .env file
RUN mkdir -p /app/config

# Expose the MCP server port
EXPOSE 3846

# Run the MCP server
CMD ["python", "-m", "confluence_mcp.main"]
