#!/usr/bin/env python3
"""
OpenAI Memory Context Test - Check if OpenAI MCP maintains conversation context
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def create_memory_test_config():
    """Configuration optimized for testing memory context"""
    return {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "tools": create_example_tools(),  # Keep local tools available
        "enable_mcp": True,
        "mcp_servers": [{
            "type": "url",
            "url": "https://mcp.pipedream.net/9fa309c7-d3d2-48e3-8236-b9732cac712c/openai",
            "name": "pipedream-openai"
        }],
        "system_prompt": """You have access to both local tools and OpenAI MCP services.

MEMORY TEST INSTRUCTIONS:
1. When testing memory, use OpenAI's assistant or chat functions to maintain context
2. Ask the user to remember specific information from previous interactions  
3. Test if OpenAI can recall information from earlier in the conversation
4. Be explicit about testing memory/context retention capabilities
5. Try to use OpenAI's thread management if available

Your goal is to determine if OpenAI maintains conversation context and memory.""",
        "debug": False
    }

def test_openai_memory_simple():
    """Test basic memory retention across interactions"""
    
    print("🧠 OPENAI MEMORY TEST - SIMPLE")
    print("=" * 50)
    
    config = create_memory_test_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    # Test sequence: establish context, then test recall
    memory_tests = [
        {
            "step": 1,
            "query": "Please remember this important fact: My favorite color is purple and my lucky number is 42. Use OpenAI to store this information.",
            "expected": "Should store the information in context"
        },
        {
            "step": 2, 
            "query": "What is my favorite color that I just told you?",
            "expected": "Should recall: purple"
        },
        {
            "step": 3,
            "query": "And what was my lucky number?", 
            "expected": "Should recall: 42"
        },
        {
            "step": 4,
            "query": "Can you tell me both pieces of information I shared with you?",
            "expected": "Should recall both: purple and 42"
        }
    ]
    
    for test in memory_tests:
        print(f"\n--- Step {test['step']}: Memory Test ---")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")
        print("-" * 40)
        
        response, err = llm.Call(test['query'], verbose=True)
        if err:
            print(f"❌ Error: {err}")
            return
        else:
            print(f"✅ Response: {response['content'][:500]}...")
            
            tools_used = response.get('tool_calls_made', [])
            if tools_used:
                print(f"🔧 Tools used: {[tool['tool'] for tool in tools_used]}")
            else:
                print("🔧 No tools used (direct response)")
        
        print()
        
        # Brief pause between tests
        input("Press Enter to continue to next memory test...")

def test_openai_thread_management():
    """Test OpenAI's thread management capabilities"""
    
    print("\n🧵 OPENAI THREAD MANAGEMENT TEST")
    print("=" * 50)
    
    config = create_memory_test_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    thread_tests = [
        {
            "step": 1,
            "query": "Please use OpenAI's thread or assistant functionality to start a new conversation thread. Tell me about the weather in Tokyo, and remember that this is for my business trip planning.",
            "expected": "Should create thread and get weather info"
        },
        {
            "step": 2,
            "query": "Based on our conversation thread, what was the context of my weather request?",
            "expected": "Should recall: business trip planning"
        },
        {
            "step": 3,
            "query": "Using the same thread, what city's weather did I ask about?",
            "expected": "Should recall: Tokyo"
        }
    ]
    
    for test in thread_tests:
        print(f"\n--- Step {test['step']}: Thread Test ---")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")
        print("-" * 40)
        
        response, err = llm.Call(test['query'], verbose=True)
        if err:
            print(f"❌ Error: {err}")
            return
        else:
            print(f"✅ Response: {response['content'][:500]}...")
            
            tools_used = response.get('tool_calls_made', [])
            if tools_used:
                print(f"🔧 Tools used: {[tool['tool'] for tool in tools_used]}")
                
                # Show tool details
                for tool in tools_used:
                    if 'thread' in tool['tool'].lower() or 'assistant' in tool['tool'].lower():
                        print(f"   📋 {tool['tool']}: {tool['input']}")
        print()
        
        input("Press Enter to continue...")

def test_openai_conversation_continuity():
    """Test conversation continuity over multiple complex interactions"""
    
    print("\n💬 OPENAI CONVERSATION CONTINUITY TEST")
    print("=" * 50)
    
    config = create_memory_test_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    continuity_tests = [
        {
            "step": 1,
            "query": "I'm planning a project called 'Neptune Analytics'. Use OpenAI to help me brainstorm 3 key features for this data analysis platform. Please remember the project name and features.",
            "expected": "Should brainstorm features and remember project details"
        },
        {
            "step": 2,
            "query": "What was the name of the project we were just discussing?",
            "expected": "Should recall: Neptune Analytics"
        },
        {
            "step": 3,
            "query": "Can you list the key features we brainstormed for my project?",
            "expected": "Should recall the 3 features discussed"
        },
        {
            "step": 4,
            "query": "Now let's add a fourth feature to our project. What would you suggest that complements the existing features?",
            "expected": "Should build on previous features contextually"
        }
    ]
    
    for test in continuity_tests:
        print(f"\n--- Step {test['step']}: Continuity Test ---")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")
        print("-" * 40)
        
        response, err = llm.Call(test['query'], verbose=True)
        if err:
            print(f"❌ Error: {err}")
            return
        else:
            print(f"✅ Response: {response['content'][:600]}...")
            
            tools_used = response.get('tool_calls_made', [])
            if tools_used:
                print(f"🔧 Tools used: {[tool['tool'] for tool in tools_used]}")
        
        print()
        input("Press Enter to continue...")

def analyze_memory_results():
    """Analyze and summarize memory test results"""
    
    print("\n📊 MEMORY TEST ANALYSIS")
    print("=" * 50)
    
    config = create_memory_test_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    analysis_query = """Based on our memory testing session, please analyze:

1. Did OpenAI successfully maintain context between interactions?
2. Were you able to use any OpenAI thread or assistant features?
3. What memory/context capabilities did you discover?
4. How does OpenAI's memory compare to your own conversation memory?
5. What are the practical implications for building applications?

Provide a comprehensive analysis of OpenAI's memory and context capabilities."""
    
    print("Query: Analyzing memory test results...")
    print("-" * 30)
    
    response, err = llm.Call(analysis_query, verbose=False)
    if err:
        print(f"❌ Error: {err}")
    else:
        print(f"✅ Analysis:\n{response['content']}")
        
        tools_used = response.get('tool_calls_made', [])
        if tools_used:
            print(f"\n🔧 Analysis tools used: {[tool['tool'] for tool in tools_used]}")

def main():
    """Main function to run OpenAI memory tests"""
    
    print("🧠 OPENAI MEMORY CONTEXT TESTING")
    print("Testing if OpenAI MCP maintains conversation memory")
    print("=" * 70)
    
    try:
        print("\nThis test will check if OpenAI can:")
        print("✓ Remember information across interactions")
        print("✓ Maintain conversation threads")
        print("✓ Build on previous context")
        print("✓ Use assistant/thread management features")
        print("\nPress Ctrl+C to stop at any time.")
        print("=" * 50)
        
        # Run memory tests
        test_openai_memory_simple()
        test_openai_thread_management()
        test_openai_conversation_continuity()
        
        # Analyze results
        analyze_memory_results()
        
        print("\n" + "=" * 70)
        print("🎉 OPENAI MEMORY TESTING COMPLETE!")
        print("✅ Tested basic memory retention")
        print("✅ Tested thread management")
        print("✅ Tested conversation continuity")
        print("✅ Provided comprehensive analysis")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Memory testing stopped by user")
    except Exception as e:
        print(f"❌ Error during memory testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()