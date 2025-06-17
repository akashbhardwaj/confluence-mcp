#!/bin/bash

# Create a local directory for tools if it doesn't exist
mkdir -p .tools/bin

# Platform detection
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [[ $(uname -m) == "arm64" ]]; then
        UV_PLATFORM="aarch64-apple-darwin"
    else
        UV_PLATFORM="x86_64-apple-darwin"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    UV_PLATFORM="x86_64-unknown-linux-gnu"
else
    echo "Unsupported platform: $OSTYPE"
    exit 1
fi

# Download uv binary
UV_VERSION="0.7.11"
UV_URL="https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-${UV_PLATFORM}.tar.gz"
echo "Downloading uv ${UV_VERSION} for ${UV_PLATFORM}..."

curl -L "$UV_URL" -o .tools/uv.tar.gz
tar -xzf .tools/uv.tar.gz -C .tools/
find .tools -name "uv" -type f -exec cp {} .tools/bin/uv \;
chmod +x .tools/bin/uv
rm .tools/uv.tar.gz

# Create virtual environment using local uv
.tools/bin/uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies using uv
uv pip install -e ".[dev]"

# Make sure we have the correct FastMCP version
uv pip install fastmcp>=2.0.0,<3.0.0

# Install pre-commit hooks
if [ -f .pre-commit-config.yaml ]; then
    pre-commit install
fi