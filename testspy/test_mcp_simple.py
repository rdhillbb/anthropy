#!/usr/bin/env python3
"""
Simple MCP test to check SDK support
"""

import anthropic
import os

def test_mcp_direct():
    """Test MCP directly with minimal code"""
    
    client = anthropic.Anthropic()
    
    try:
        # Try direct API call with MCP parameters
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": "Hello, do you have access to any tools?"}],
            mcp_servers=[{
                "type": "url",
                "url": "https://mcp.pipedream.net/9fa309c7-d3d2-48e3-8236-b9732cac712c/openai",
                "name": "pipedream-openai"
            }],
            extra_headers={"anthropic-beta": "mcp-client-2025-04-04"}
        )
        
        print("✅ MCP call successful!")
        print(f"Response: {response.content[0].text}")
        
    except Exception as e:
        print(f"❌ MCP call failed: {e}")
        
        # Try without MCP as fallback
        print("\n🔄 Trying fallback without MCP...")
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": "Hello, this is a test without MCP."}]
            )
            
            print("✅ Regular call successful!")
            print(f"Response: {response.content[0].text}")
            
        except Exception as e2:
            print(f"❌ Regular call also failed: {e2}")

if __name__ == "__main__":
    test_mcp_direct()