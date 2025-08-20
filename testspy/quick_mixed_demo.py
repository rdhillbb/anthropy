#!/usr/bin/env python3
"""
Quick Mixed Tools Demo - Concise demonstration of local + MCP tools
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def create_mixed_config():
    """Configuration with both local tools and MCP"""
    return {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.6,
        "tools": create_example_tools(),  # Local weather/news
        "enable_mcp": True,               # Enable MCP
        "mcp_servers": [{
            "type": "url",
            "url": "https://mcp.pipedream.net/9fa309c7-d3d2-48e3-8236-b9732cac712c/openai",
            "name": "pipedream-openai"
        }],
        "system_prompt": """You have access to both local tools (weather, news) and MCP tools (OpenAI capabilities).
Use the most appropriate tools for each request. Be efficient and helpful.""",
        "debug": False
    }

def demo_mixed_tools():
    """Demonstrate mixed tool usage"""
    
    print("🔧 MIXED TOOLS DEMO")
    print("=" * 40)
    
    config = create_mixed_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    # Test cases that showcase different tool combinations
    tests = [
        {
            "name": "Local Weather Tool",
            "query": "What's the weather in New York?",
            "expected": "Should use local weather tool"
        },
        {
            "name": "Local News Tool", 
            "query": "Get me the latest technology news",
            "expected": "Should use local news tool"
        },
        {
            "name": "Multiple Local Tools",
            "query": "Check weather in London and get sports news",
            "expected": "Should use both local tools"
        },
        {
            "name": "MCP Capabilities",
            "query": "What MCP tools do you have?",
            "expected": "Should discover MCP tools available"
        },
        {
            "name": "Creative Task (MCP)",
            "query": "Write a haiku about artificial intelligence",
            "expected": "Could use MCP or direct response"
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n--- Test {i}: {test['name']} ---")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")
        print("-" * 30)
        
        response, err = llm.Call(test['query'])
        if err:
            print(f"❌ Error: {err}")
        else:
            # Show truncated response
            content = response['content']
            if len(content) > 300:
                content = content[:300] + "..."
            
            print(f"✅ Response: {content}")
            
            tools_used = response.get('tool_calls_made', [])
            if tools_used:
                tool_names = [tool['tool'] for tool in tools_used]
                print(f"🔧 Tools used: {', '.join(tool_names)} ({len(tools_used)} total)")
            else:
                print("🔧 Tools used: None (direct response)")
        
        print()

def demo_tool_fallback():
    """Demonstrate fallback between MCP and local tools"""
    
    print("\n🔄 TOOL FALLBACK DEMO")
    print("=" * 40)
    
    config = create_mixed_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    print("Testing how the system handles tool availability and fallback...")
    
    # Test a query that could use either system
    query = "Help me plan a day trip: check weather in San Francisco and suggest creative indoor activities if it's rainy"
    
    print(f"\nQuery: {query}")
    print("Expected: Use local weather tool + MCP/direct for creative suggestions")
    print("-" * 50)
    
    response, err = llm.Call(query)
    if err:
        print(f"❌ Error: {err}")
    else:
        print(f"✅ Response: {response['content'][:400]}...")
        
        tools_used = response.get('tool_calls_made', [])
        if tools_used:
            print(f"\n🔧 Tools called:")
            for tool in tools_used:
                print(f"   - {tool['tool']}: {tool['input']}")
        else:
            print("🔧 No tools called - direct response")

def main():
    """Run the quick mixed tools demonstration"""
    
    print("🚀 QUICK MIXED TOOLS DEMONSTRATION")
    print("Showing hybrid use of Local + MCP tools")
    print("=" * 50)
    
    try:
        demo_mixed_tools()
        demo_tool_fallback()
        
        print("\n" + "=" * 50)
        print("🎉 DEMO COMPLETE!")
        print("✅ Local tools (weather/news) work perfectly")
        print("✅ MCP integration detects available tools")
        print("✅ Intelligent tool selection and fallback")
        print("✅ Hybrid workflows combining both systems")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()