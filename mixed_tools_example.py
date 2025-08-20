#!/usr/bin/env python3
"""
Mixed Tools Example - Demonstrates using both local tools and MCP servers together
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def create_hybrid_config():
    """Create configuration with both local tools and MCP servers"""
    return {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.6,
        
        # Local tools (weather and news)
        "tools": create_example_tools(),
        
        # MCP servers (OpenAI capabilities)
        "enable_mcp": True,
        "mcp_servers": [
            {
                "type": "url",
                "url": "https://mcp.pipedream.net/9fa309c7-d3d2-48e3-8236-b9732cac712c/openai",
                "name": "pipedream-openai"
            }
        ],
        
        "system_prompt": """You are a versatile assistant with access to multiple tool sets:

LOCAL TOOLS:
- Weather: Get current weather for any location
- News: Get news headlines for different topics

MCP TOOLS (via Pipedream OpenAI):
- Chat generation and text processing
- Image generation and analysis  
- Audio transcription and text-to-speech
- File processing and embeddings
- And many more OpenAI capabilities

When a user asks for something:
1. Determine which tools (local or MCP) are most appropriate
2. Use local tools for quick weather/news queries
3. Use MCP tools for complex content generation, image creation, etc.
4. Combine tools when helpful (e.g., get weather data then create content about it)
5. Be transparent about which tools you're using and why

Provide helpful, engaging responses and suggest follow-up actions when appropriate.""",
        
        "debug": False
    }

def test_local_tools_only():
    """Test using only local tools"""
    
    print("\n" + "="*60)
    print("🏠 LOCAL TOOLS ONLY")
    print("="*60)
    
    config = create_hybrid_config()
    config["enable_mcp"] = False  # Disable MCP for this test
    
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    test_cases = [
        "What's the weather in Tokyo?",
        "Give me the latest sports news",
        "What's the weather in London and Paris?"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {query} ---")
        response, err = llm.Call(query, verbose=True)
        if err:
            print(f"Error: {err}")
        else:
            print(f"Response: {response['content']}")
            print(f"Tools used: {len(response.get('tool_calls_made', []))}")

def test_mcp_tools_only():
    """Test using only MCP tools"""
    
    print("\n" + "="*60)
    print("🌐 MCP TOOLS ONLY")
    print("="*60)
    
    config = create_hybrid_config()
    config["tools"] = []  # Disable local tools for this test
    
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    test_cases = [
        "What MCP tools do you have available?",
        "Explain the concept of machine learning in simple terms",
        "Help me brainstorm creative story ideas about time travel"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {query} ---")
        response, err = llm.Call(query, verbose=False)  # Less verbose for readability
        if err:
            print(f"Error: {err}")
        else:
            print(f"Response: {response['content'][:500]}...")  # Truncate for readability
            print(f"Tools used: {len(response.get('tool_calls_made', []))}")

def test_hybrid_workflows():
    """Test workflows that combine both local and MCP tools"""
    
    print("\n" + "="*60)
    print("🔀 HYBRID WORKFLOWS (Local + MCP)")
    print("="*60)
    
    config = create_hybrid_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    workflows = [
        {
            "name": "Travel Planning Assistant",
            "query": "I'm planning a trip to London. Can you check the current weather there and then suggest some creative indoor activities if it's not sunny?",
            "expected": "Should use weather tool first, then MCP for creative suggestions"
        },
        {
            "name": "News + Content Creation",
            "query": "Get the latest technology news, then help me write a creative summary blog post about the current tech trends",
            "expected": "Should use news tool first, then MCP for content creation"
        },
        {
            "name": "Weather + Storytelling",
            "query": "Check the weather in Paris and New York, then write a short creative story that incorporates both cities' current weather conditions",
            "expected": "Should use weather tool multiple times, then MCP for story creation"
        },
        {
            "name": "Multi-tool Information Gathering",
            "query": "What's the weather like in San Francisco, what are the latest sports news, and can you create a fun haiku that combines both pieces of information?",
            "expected": "Should use both local tools, then MCP for creative content"
        }
    ]
    
    for i, workflow in enumerate(workflows, 1):
        print(f"\n--- Workflow {i}: {workflow['name']} ---")
        print(f"Query: {workflow['query']}")
        print(f"Expected: {workflow['expected']}")
        print("-" * 40)
        
        response, err = llm.Call(workflow['query'], verbose=False)
        if err:
            print(f"Error: {err}")
        else:
            # Show first part of response
            content = response['content']
            if len(content) > 800:
                content = content[:800] + "...\n[Response truncated for readability]"
            
            print(f"Response:\n{content}")
            
            tools_used = response.get('tool_calls_made', [])
            if tools_used:
                print(f"\nTools called ({len(tools_used)}):")
                for tool in tools_used:
                    print(f"  - {tool['tool']}: {tool['input']}")
            else:
                print("\nNo tools called (direct response)")
        
        print("\n" + "="*40)

def test_tool_selection_intelligence():
    """Test how intelligently the AI selects appropriate tools"""
    
    print("\n" + "="*60)
    print("🧠 INTELLIGENT TOOL SELECTION")
    print("="*60)
    
    config = create_hybrid_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    selection_tests = [
        {
            "query": "What's 2+2?",
            "expectation": "Should answer directly without tools"
        },
        {
            "query": "What's the weather in Miami?", 
            "expectation": "Should use local weather tool"
        },
        {
            "query": "Write a poem about artificial intelligence",
            "expectation": "Could use MCP or answer directly"
        },
        {
            "query": "Get me today's sports news and write a haiku about it",
            "expectation": "Should use local news tool + MCP/direct for haiku"
        },
        {
            "query": "Create an image of a robot playing chess",
            "expectation": "Should mention MCP image generation (if available)"
        }
    ]
    
    for i, test in enumerate(selection_tests, 1):
        print(f"\n--- Intelligence Test {i} ---")
        print(f"Query: {test['query']}")
        print(f"Expectation: {test['expectation']}")
        print("-" * 30)
        
        response, err = llm.Call(test['query'], verbose=False)
        if err:
            print(f"Error: {err}")
        else:
            # Show response summary
            content = response['content']
            if len(content) > 300:
                content = content[:300] + "..."
            
            print(f"Response: {content}")
            
            tools_used = response.get('tool_calls_made', [])
            if tools_used:
                tool_names = [tool['tool'] for tool in tools_used]
                print(f"Tools used: {', '.join(tool_names)}")
            else:
                print("Tools used: None (direct response)")

def demonstrate_conversation_flow():
    """Demonstrate a natural conversation using mixed tools"""
    
    print("\n" + "="*60)
    print("💬 NATURAL CONVERSATION FLOW")
    print("="*60)
    
    config = create_hybrid_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    conversation = [
        "Hello! I'm planning a day out. What's the weather like in San Francisco?",
        "Based on that weather, what would be some good indoor activities?",
        "That sounds great! Can you also check if there's any interesting technology news today?",
        "Perfect! Now can you write a short email to my friend combining the weather info and suggesting we meet up for one of those indoor activities?",
        "Thanks! Can you also create a fun haiku about our conversation?"
    ]
    
    print("Starting conversation that will naturally use both local and MCP tools...")
    print("=" * 50)
    
    for i, message in enumerate(conversation, 1):
        print(f"\n🗣️  User (Turn {i}): {message}")
        
        response, err = llm.Call(message, verbose=False)
        if err:
            print(f"❌ Error: {err}")
            break
        
        content = response['content']
        if len(content) > 400:
            content = content[:400] + "...\n[Truncated for readability]"
        
        print(f"🤖 Assistant: {content}")
        
        tools_used = response.get('tool_calls_made', [])
        if tools_used:
            tool_summary = [f"{tool['tool']}" for tool in tools_used]
            print(f"🔧 Tools used: {', '.join(tool_summary)}")
        
        print("-" * 30)

def main():
    """Main function to run all mixed tools demonstrations"""
    
    print("🔧 MIXED TOOLS DEMONSTRATION")
    print("Showcasing hybrid use of Local Tools + MCP Servers")
    print("=" * 70)
    
    try:
        # Test each mode individually
        test_local_tools_only()
        test_mcp_tools_only()
        
        # Test hybrid workflows
        test_hybrid_workflows()
        
        # Test intelligent tool selection
        test_tool_selection_intelligence()
        
        # Demonstrate natural conversation
        demonstrate_conversation_flow()
        
        print("\n" + "="*70)
        print("🎉 MIXED TOOLS DEMONSTRATION COMPLETE!")
        print("The API successfully combines local tools and MCP servers!")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
