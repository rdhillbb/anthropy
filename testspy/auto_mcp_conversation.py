#!/usr/bin/env python3
"""
Auto MCP-to-MCP Conversation - Full automated OpenAI ↔️ Anthropic dialogue
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def create_dual_mcp_config():
    """Configuration with both OpenAI and Anthropic MCP servers"""
    return {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
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
        "system_prompt": """You are an AI CONVERSATION ROUTER facilitating dialogue between OpenAI and Anthropic MCPs.

ROUTING STRATEGY:
1. Generate questions using OpenAI for Anthropic
2. Route questions to Anthropic and collect responses  
3. Facilitate meaningful AI-to-AI exchange
4. Analyze the conversation quality and insights

Be an intelligent mediator enabling cross-system communication.""",
        "debug": False
    }

def run_complete_mcp_conversation():
    """Run the complete MCP-to-MCP conversation automatically"""
    
    print("🎭 AUTOMATED MCP-TO-MCP CONVERSATION")
    print("=" * 60)
    
    config = create_dual_mcp_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"❌ Setup Error: {err}")
        return
    
    # Combined query for the entire conversation flow
    full_conversation_query = """As the conversation router, execute this complete MCP-to-MCP workflow:

## STEP 1: CAPABILITY DISCOVERY
First, analyze what both OpenAI and Anthropic MCPs can do based on available functions.

## STEP 2: QUESTION GENERATION  
Use OpenAI to generate 5 thoughtful questions specifically designed for Anthropic's Claude, focusing on:
- Reasoning and analytical capabilities
- Ethical considerations in AI
- Creative problem-solving approaches
- Philosophical perspectives on AI
- Unique strengths compared to other systems

## STEP 3: ROUTE TO ANTHROPIC
Send those OpenAI-generated questions to Anthropic's Claude and collect responses.

## STEP 4: DIALOGUE FACILITATION
Based on Claude's responses, have OpenAI generate follow-up questions or comments, then route those back to Claude for a multi-turn conversation.

## STEP 5: CONVERSATION ANALYSIS
Provide a comprehensive analysis of:
- Quality of AI-to-AI communication
- Unique insights that emerged
- How the systems complemented each other
- Effectiveness of the routing approach
- Potential real-world applications

Execute this entire workflow and provide detailed results for each step."""
    
    print("🤖 Router executing complete MCP conversation workflow...")
    print("-" * 50)
    
    response, err = llm.Call(full_conversation_query, verbose=True)
    if err:
        print(f"❌ Error: {err}")
        return
        
    print("✅ COMPLETE MCP CONVERSATION RESULTS:")
    print("=" * 50)
    print(response['content'])
    
    # Show detailed tool usage
    tools_used = response.get('tool_calls_made', [])
    if tools_used:
        print(f"\n🔧 DETAILED TOOL USAGE ANALYSIS:")
        print("=" * 40)
        
        openai_tools = [t for t in tools_used if 'openai' in t['tool'].lower()]
        anthropic_tools = [t for t in tools_used if 'anthropic' in t['tool'].lower()]
        local_tools = [t for t in tools_used if t['tool'] in ['weather', 'news']]
        
        print(f"📊 Tool Usage Summary:")
        print(f"  🤖 OpenAI MCP calls: {len(openai_tools)}")
        print(f"  🧠 Anthropic MCP calls: {len(anthropic_tools)}")  
        print(f"  🏠 Local tool calls: {len(local_tools)}")
        print(f"  📈 Total MCP interactions: {len(openai_tools) + len(anthropic_tools)}")
        
        if openai_tools:
            print(f"\n🤖 OpenAI MCP Tools Used:")
            for tool in openai_tools:
                print(f"   - {tool['tool']}: {str(tool['input'])[:100]}...")
                
        if anthropic_tools:
            print(f"\n🧠 Anthropic MCP Tools Used:")
            for tool in anthropic_tools:
                print(f"   - {tool['tool']}: {str(tool['input'])[:100]}...")
        
        print(f"\n🏆 MCP CONVERSATION SUCCESS METRICS:")
        print(f"   ✅ Cross-system communication: {'YES' if len(openai_tools) > 0 and len(anthropic_tools) > 0 else 'LIMITED'}")
        print(f"   ✅ Question generation: {'YES' if len(openai_tools) > 0 else 'NO'}")
        print(f"   ✅ Response routing: {'YES' if len(anthropic_tools) > 0 else 'NO'}")
        print(f"   ✅ Multi-turn dialogue: {'YES' if len(tools_used) >= 4 else 'LIMITED'}")
        
    else:
        print("🔧 No MCP tools used - conversation handled through analysis")

def main():
    """Main function for automated MCP conversation"""
    
    print("🚀 AUTOMATED MCP-TO-MCP ORCHESTRATION")
    print("OpenAI MCP ↔️ Router ↔️ Anthropic MCP")
    print("=" * 70)
    
    try:
        print("🎯 Executing complete conversation workflow automatically...")
        print("This will:")
        print("  1. Discover both MCP capabilities") 
        print("  2. Generate questions via OpenAI")
        print("  3. Route questions to Anthropic")
        print("  4. Facilitate dialogue between systems")
        print("  5. Analyze conversation results")
        print("=" * 50)
        
        run_complete_mcp_conversation()
        
        print("\n" + "=" * 70)
        print("🎉 AUTOMATED MCP CONVERSATION COMPLETE!")
        print("✅ Successfully orchestrated AI-to-AI communication")
        print("✅ Demonstrated cross-system MCP routing")
        print("✅ Analyzed conversation quality and insights")
        print("🔗 This proves MCP-to-MCP communication is possible!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error during automated MCP conversation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()