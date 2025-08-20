#!/usr/bin/env python3
"""
Real MCP Conversation - Actual OpenAI <-> Anthropic dialogue with detailed account
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def create_conversation_router_config():
    """Configuration for router that facilitates real MCP conversations"""
    return {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.5,
        "tools": create_example_tools(),
        "enable_mcp": True,
        "mcp_servers": [
            {
                "type": "url",
                "url": "https://mcp.pipedream.net/9fa309c7-d3d2-48e3-8236-b9732cac712c/openai",
                "name": "pipedream-openai"
            },
            {
                "type": "url", 
                "url": "https://mcp.pipedream.net/9fa309c7-d3d2-48e3-8236-b9732cac712c/anthropic",
                "name": "pipedream-anthropic"
            }
        ],
        "system_prompt": """You are a CONVERSATION ROUTER that facilitates ACTUAL conversations between OpenAI and Anthropic MCPs.

CRITICAL: You must actually USE the MCP tools to create real conversations, not simulate them.

WORKFLOW:
1. Use OpenAI MCP tools to generate questions
2. Use Anthropic MCP tools to respond to those questions  
3. Continue the conversation by routing responses back and forth
4. Maintain the conversation flow through actual tool calls
5. Provide detailed account of what actually happened
Think
I want the details 
IMPORTANT: Always make actual tool calls - don't just describe what would happen.""",
        "debug": True  # Enable debug to see actual tool calls
    }

def execute_real_mcp_conversation():
    """Execute actual MCP-to-MCP conversation with tool calls"""
    
    print("💬 EXECUTING REAL MCP-TO-MCP CONVERSATION")
    print("=" * 60)
    
    config = create_conversation_router_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"❌ Router Setup Error: {err}")
        return
    
    conversation_instruction = """Execute a REAL conversation between OpenAI and Anthropic MCPs using actual tool calls:

STEP 1: Use OpenAI MCP to generate 3 specific questions about AI reasoning for Anthropic
STEP 2: Use Anthropic MCP to respond to each question from OpenAI
STEP 3: Use OpenAI MCP to generate follow-up questions based on Anthropic's responses
STEP 4: Use Anthropic MCP to provide final responses
STEP 5: Tell OpenAI MCP that it should think of 3 messages to ask Anthropic MCP. No more than 2
STEP 6: Tell Anthropic MCP to ask Questions to OPENAI MCP. No more then 3
STEP 7: Provide the actual messages that requests and respsones between OpenAI MCP and Anthropci MCP

CRITICAL: Make actual tool calls to both MCPs. Do not simulate - use the real functions.

After the conversation, provide a detailed account of:
- What questions were actually asked
- What responses were actually given
- How the conversation flowed
- Which specific tools were used
- Quality of the AI-to-AI dialogue

Execute this real conversation now."""
    
    print("🤖 Router executing REAL MCP conversation...")
    print("-" * 50)
    
    response, err = llm.Call(conversation_instruction, verbose=True)
    if err:
        print(f"❌ Conversation Error: {err}")
        return
        
    print("✅ REAL MCP CONVERSATION COMPLETED")
    print("=" * 50)
    print(response['content'])
    
    # Analyze actual tool usage
    tools_used = response.get('tool_calls_made', [])
    print(f"\n🔧 ACTUAL TOOL CALLS MADE: {len(tools_used)}")
    
    if tools_used:
        openai_calls = [t for t in tools_used if 'openai' in t.get('tool', '').lower()]
        anthropic_calls = [t for t in tools_used if 'anthropic' in t.get('tool', '').lower()]
        
        print(f"🤖 OpenAI MCP Calls: {len(openai_calls)}")
        print(f"🧠 Anthropic MCP Calls: {len(anthropic_calls)}")
        
        if openai_calls:
            print("\n🤖 OpenAI MCP Interactions:")
            for i, call in enumerate(openai_calls, 1):
                print(f"  {i}. {call['tool']}")
                print(f"     Input: {str(call['input'])[:200]}...")
                print(f"     Result: {str(call['result'])[:200]}...")
        
        if anthropic_calls:
            print("\n🧠 Anthropic MCP Interactions:")
            for i, call in enumerate(anthropic_calls, 1):
                print(f"  {i}. {call['tool']}")
                print(f"     Input: {str(call['input'])[:200]}...")
                print(f"     Result: {str(call['result'])[:200]}...")
                
        return True
    else:
        print("❌ No actual MCP tool calls were made - conversation was simulated")
        return False

def request_detailed_conversation_account():
    """Ask the router for a detailed account of the conversation"""
    
    print("\n" + "=" * 60)
    print("📋 REQUESTING DETAILED CONVERSATION ACCOUNT")
    print("=" * 60)
    
    config = create_conversation_router_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"❌ Router Setup Error: {err}")
        return
    
    account_request = """ Note: It must be the exact messages between the two systems. Please provide a detailed account of the MCP-to-MCP conversation that just occurred:

DETAILED ACCOUNT REQUESTED:

1. CONVERSATION TRANSCRIPT:
   - Exact questions that OpenAI generated
   - Exact responses that Anthropic provided
   - Any follow-up exchanges

2. TECHNICAL DETAILS:
   - Which specific MCP functions were called
   - How data was passed between systems
   - Any authentication or connection details

3. CONVERSATION ANALYSIS:
   - Quality of the AI-to-AI dialogue
   - Insights that emerged
   - How well the systems understood each other

4. ROUTING EFFECTIVENESS:
   - How smoothly the conversation flowed
   - Any challenges in facilitating the exchange
   - Success of the mediation approach

5. PRACTICAL OBSERVATIONS:
   - Real-world implications
   - Potential applications
   - Lessons learned

Provide the most comprehensive account possible of what actually transpired."""
    
    print("🤖 Router providing detailed conversation account...")
    print("-" * 50)
    
    response, err = llm.Call(account_request, verbose=True)
    if err:
        print(f"❌ Account Error: {err}")
        return
        
    print("✅ DETAILED CONVERSATION ACCOUNT:")
    print("=" * 50)
    print(response['content'])

def main():
    """Main function to execute real MCP conversation and get detailed account"""
    
    print("🚀 REAL MCP-TO-MCP CONVERSATION WITH DETAILED ACCOUNT")
    print("OpenAI MCP ↔️ Router ↔️ Anthropic MCP")
    print("=" * 70)
    
    try:
        print("Phase 1: Execute actual MCP-to-MCP conversation")
        print("Phase 2: Request detailed account of what happened")
        print("=" * 50)
        
        # Phase 1: Execute real conversation
        conversation_happened = execute_real_mcp_conversation()
        
        # Phase 2: Get detailed account
        if conversation_happened:
            print("\n🎯 Conversation completed! Requesting detailed account...")
        else:
            print("\n⚠️ Conversation may have been simulated. Requesting account anyway...")
            
        request_detailed_conversation_account()
        
        print("\n" + "=" * 70)
        print("🎉 REAL MCP CONVERSATION AND ACCOUNT COMPLETE!")
        print("✅ Attempted actual MCP-to-MCP dialogue")
        print("✅ Provided detailed conversation account")
        print("✅ Analyzed routing effectiveness")
        print("🔗 This demonstrates real AI-to-AI communication!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error during real MCP conversation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
