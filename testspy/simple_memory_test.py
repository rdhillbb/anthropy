#!/usr/bin/env python3
"""
Simple OpenAI Memory Test - Ask question, then test recall
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def simple_memory_test():
    config = {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "tools": create_example_tools(),
        "enable_mcp": True,
        "mcp_servers": [{
            "type": "url",
            "url": "https://mcp.pipedream.net/9fa309c7-d3d2-48e3-8236-b9732cac712c/openai",
            "name": "pipedream-openai"
        }],
        "system_prompt": "Use OpenAI tools to test memory retention. Remember information between interactions.",
        "debug": False
    }
    
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    print("🧠 SIMPLE MEMORY TEST")
    print("=" * 30)
    
    # Step 1: Give information
    print("\n1️⃣ Telling OpenAI information to remember...")
    response1, err1 = llm.Call("Remember this: My name is Alice and I live in Seattle.")
    
    if err1:
        print(f"❌ Error: {err1}")
        return
        
    print(f"Response: {response1['content'][:200]}...")
    
    # Step 2: Test recall
    print("\n2️⃣ Testing if OpenAI remembers...")
    response2, err2 = llm.Call("What did I just tell you to remember?")
    
    if err2:
        print(f"❌ Error: {err2}")
        return
        
    print(f"Response: {response2['content']}")
    
    # Show tools used
    tools1 = response1.get('tool_calls_made', [])
    tools2 = response2.get('tool_calls_made', [])
    
    print(f"\n🔧 Tools used:")
    print(f"  Step 1: {[t['tool'] for t in tools1] if tools1 else 'None'}")
    print(f"  Step 2: {[t['tool'] for t in tools2] if tools2 else 'None'}")

if __name__ == "__main__":
    simple_memory_test()