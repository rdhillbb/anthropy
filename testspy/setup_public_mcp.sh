#!/bin/bash
# Setup Public MCP Server Access
echo "🌐 Setting up public access to local MCP server"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found. Installing ngrok..."
    
    # Install ngrok via homebrew (macOS)
    if command -v brew &> /dev/null; then
        brew install ngrok/ngrok/ngrok
    else
        echo "📥 Please install ngrok manually:"
        echo "   https://ngrok.com/download"
        echo "   brew install ngrok/ngrok/ngrok"
        exit 1
    fi
fi

echo "✅ ngrok found"

# Check if MCP server is running
echo "🔍 Checking if MCP server is running on localhost:8000..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ MCP server is running"
else
    echo "❌ MCP server not running on localhost:8000"
    echo "💡 Start it first: ./start_mcp_server.sh"
    exit 1
fi

echo "🚀 Starting ngrok tunnel..."
echo "This will create a public URL that Anthropic can access"
echo "Keep this terminal open while testing MCP integration"
echo ""
echo "🔗 The public URL will be displayed below"
echo "📋 Copy this URL and use it in your MCP configuration"
echo ""

# Start ngrok tunnel with specific URL
ngrok http --url=bartonsville.ngrok.app 8000