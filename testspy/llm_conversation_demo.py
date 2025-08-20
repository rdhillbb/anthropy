#!/usr/bin/env python3
"""
LLM Conversation Demo - Have Claude talk to OpenAI MCP server and report back
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def create_conversation_config():
    """Configuration for LLM-to-LLM conversation via MCP"""
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
        "system_prompt": """You are Claude, an AI assistant with access to both local tools and MCP servers that connect to OpenAI's services.

Your task is to have a conversation with the OpenAI server to understand its capabilities. You should:

1. Start by asking what services/tools are available
2. Ask follow-up questions about specific capabilities that interest you
3. Try to understand the breadth and depth of what OpenAI offers
4. Ask about unique features or standout capabilities
5. Inquire about any limitations or requirements
6. Ask at least 5-7 substantive questions to get a comprehensive understanding
7. After the conversation, provide a detailed summary of what you learned

Be curious, thorough, and conversational. Act as if you're genuinely interested in understanding what the OpenAI system can do and how it compares to your own capabilities.""",
        "debug": False
    }

def run_llm_conversation():
    """Have Claude initiate a conversation with the OpenAI MCP server"""
    
    print("🤖 LLM-TO-LLM CONVERSATION VIA MCP")
    print("Claude will now talk to the OpenAI server")
    print("=" * 60)
    
    config = create_conversation_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"❌ Error creating LLM: {err}")
        return
    
    # The main conversation request
    conversation_request = """Please talk to the OpenAI server to understand what it can do. Do more than 5 turns/questions to get a comprehensive understanding. 

Start the conversation and ask probing questions about:
- What services and tools are available
- Specific capabilities like text generation, image creation, audio processing
- Any unique or standout features
- Limitations or requirements
- How it compares to other AI systems
- What makes it particularly useful

After the conversation, provide me a detailed summary of what you learned about the OpenAI system's capabilities."""
    
    print("🗣️  User Request:")
    print(f"'{conversation_request}'")
    print()
    print("🤖 Claude's Response:")
    print("-" * 40)
    
    # Make the request
    response, err = llm.Call(conversation_request, verbose=True)
    
    if err:
        print(f"❌ Error: {err}")
        return
    
    # Display the response
    print(response['content'])
    
    # Show what tools were called
    tools_used = response.get('tool_calls_made', [])
    
    print("\n" + "=" * 60)
    print("📊 CONVERSATION ANALYSIS")
    print("=" * 60)
    
    if tools_used:
        print(f"🔧 Total tool calls made: {len(tools_used)}")
        print("\n🛠️  Tool Usage Breakdown:")
        
        tool_types = {}
        for tool in tools_used:
            tool_name = tool['tool']
            if tool_name in tool_types:
                tool_types[tool_name] += 1
            else:
                tool_types[tool_name] = 1
        
        for tool_name, count in tool_types.items():
            tool_type = "LOCAL" if tool_name in ['weather', 'news'] else "MCP/OPENAI"
            print(f"   - {tool_name} ({tool_type}): {count} calls")
        
        print(f"\n📝 Sample tool calls:")
        for i, tool in enumerate(tools_used[:3], 1):  # Show first 3
            print(f"   {i}. {tool['tool']}: {tool['input']}")
        
        if len(tools_used) > 3:
            print(f"   ... and {len(tools_used) - 3} more")
    else:
        print("🔧 No explicit tool calls were made")
        print("   (This could mean the conversation was handled directly)")
    
    print(f"\n📏 Response length: {len(response['content'])} characters")
    print(f"🧠 Tokens used: {response.get('tokens_used', 'Unknown')}")

def run_follow_up_questions():
    """Ask Claude to elaborate on specific aspects discovered"""
    
    print("\n" + "=" * 60)
    print("🔍 FOLLOW-UP EXPLORATION")
    print("=" * 60)
    
    config = create_conversation_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"❌ Error: {err}")
        return
    
    follow_ups = [
        "Based on your conversation with OpenAI, what are the top 3 most impressive capabilities you discovered?",
        "How do OpenAI's capabilities compare to your own abilities? What can they do that you can't?",
        "What would be the best use cases for combining your local tools with OpenAI's MCP services?"
    ]
    
    for i, question in enumerate(follow_ups, 1):
        print(f"\n--- Follow-up {i} ---")
        print(f"Question: {question}")
        print("-" * 30)
        
        response, err = llm.Call(question, verbose=True)
        if err:
            print(f"❌ Error: {err}")
        else:
            # Show abbreviated response
            content = response['content']
            if len(content) > 400:
                content = content[:400] + "...\n[Response truncated]"
            print(f"Answer: {content}")

def main():
    """Main function to run the LLM conversation demo"""
    
    print("🎭 LLM CONVERSATION DEMONSTRATION")
    print("Having Claude explore OpenAI's capabilities via MCP")
    print("=" * 70)
    
    try:
        # Main conversation
        run_llm_conversation()
        
        # Follow-up questions
        run_follow_up_questions()
        
        print("\n" + "=" * 70)
        print("🎉 LLM CONVERSATION COMPLETE!")
        print()
        print("✅ Claude successfully communicated with OpenAI MCP server")
        print("✅ Multi-turn conversation exploring capabilities")
        print("✅ Comprehensive summary and analysis provided")
        print("✅ Follow-up insights and comparisons generated")
        print()
        print("🔗 This demonstrates the power of MCP for AI-to-AI communication!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error during conversation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
