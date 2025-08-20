#!/bin/bash
# Start MCP Server Script

echo "🚀 Starting Local MCP Server"
echo "================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements_mcp.txt

# Check environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set - OpenAI tools will be disabled"
    echo "   Set with: export OPENAI_API_KEY='your-key-here'"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set - Anthropic integration won't work"
    echo "   Set with: export ANTHROPIC_API_KEY='your-key-here'"
fi

# Start the server
echo ""
echo "🌐 Starting MCP server on http://localhost:8000"
echo "📡 MCP endpoint: http://localhost:8000/mcp"
echo "❤️  Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 mcp_server.py