#!/bin/bash
# Start Public MCP Server with ngrok

echo "🌐 STARTING PUBLIC MCP SERVER"
echo "Using ngrok URL: https://bartonsville.ngrok.app"
echo "=" * 50

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    
    # Kill ngrok if running
    pkill -f "ngrok http"
    
    # Kill MCP server if running  
    pkill -f "mcp_server.py"
    
    echo "✅ Cleanup complete"
    exit 0
}

# Set trap for cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Check if MCP server is already running
if lsof -i :8000 > /dev/null 2>&1; then
    echo "✅ MCP server already running on port 8000"
else
    echo "🚀 Starting MCP server..."
    source .venv/bin/activate
    python3 mcp_server.py &
    
    # Wait for server to start
    sleep 3
    
    if lsof -i :8000 > /dev/null 2>&1; then
        echo "✅ MCP server started on port 8000"
    else
        echo "❌ Failed to start MCP server"
        exit 1
    fi
fi

# Check if ngrok is running with our URL
if curl -s https://bartonsville.ngrok.app/health > /dev/null; then
    echo "✅ ngrok tunnel already active"
else
    echo "🌐 Starting ngrok tunnel..."
    ngrok http --url=bartonsville.ngrok.app 8000 &
    
    # Wait for ngrok to start
    echo "⏳ Waiting for ngrok tunnel to establish..."
    for i in {1..10}; do
        if curl -s https://bartonsville.ngrok.app/health > /dev/null; then
            echo "✅ ngrok tunnel established"
            break
        fi
        sleep 2
        echo "   Attempt $i/10..."
    done
    
    if ! curl -s https://bartonsville.ngrok.app/health > /dev/null; then
        echo "❌ Failed to establish ngrok tunnel"
        exit 1
    fi
fi

# Test the public endpoint
echo ""
echo "🧪 Testing public MCP server..."
response=$(curl -s https://bartonsville.ngrok.app/health)
if echo "$response" | grep -q "healthy"; then
    echo "✅ Public MCP server is healthy!"
    echo "📡 Public URL: https://bartonsville.ngrok.app"
    echo "🔧 MCP Endpoint: https://bartonsville.ngrok.app/mcp"
else
    echo "❌ Public MCP server health check failed"
    echo "Response: $response"
    exit 1
fi

echo ""
echo "🎯 MCP SERVER IS NOW PUBLIC AND READY!"
echo "=" * 50
echo "You can now run:"
echo "  python3 mixed_tools_example_v2_public.py"
echo "  python3 test_with_ngrok_url.py"
echo ""
echo "Press Ctrl+C to stop both services"
echo "=" * 50

# Keep script running
while true; do
    sleep 30
    # Health check every 30 seconds
    if ! curl -s https://bartonsville.ngrok.app/health > /dev/null; then
        echo "⚠️  Health check failed at $(date)"
        echo "🔄 Services might need restart"
    fi
done