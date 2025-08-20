#!/usr/bin/env python3
"""
MCP-to-MCP Conversation - OpenAI MCP talks to Anthropic MCP via router
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def create_dual_mcp_config():
    """Configuration with both OpenAI and Anthropic MCP servers"""
    return {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "tools": create_example_tools(),  # Keep local tools available
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
        "system_prompt": """You are an AI CONVERSATION ROUTER with access to both OpenAI and Anthropic MCP services.

Your role is to facilitate a conversation between these two AI systems:

AVAILABLE SERVICES:
- OpenAI MCP: Text generation, image creation, audio processing, embeddings, etc.
- Anthropic MCP: Claude AI capabilities, reasoning, analysis, etc.

ROUTING STRATEGY:
1. First, discover the capabilities of both MCPs
2. Have OpenAI generate questions specifically for Anthropic
3. Route those questions to Anthropic MCP and collect responses
4. Facilitate back-and-forth dialogue between the systems
5. Provide analysis and insights from their conversation

Act as an intelligent router that enables meaningful AI-to-AI communication.""",
        "debug": False
    }

def discover_mcp_capabilities():
    """Step 1: Discover capabilities of both MCPs"""
    
    print("🔍 DISCOVERING MCP CAPABILITIES")
    print("=" * 60)
    
    config = create_dual_mcp_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return None
    
    discovery_query = """As the conversation router, please discover and analyze the capabilities of both MCP services:

1. OPENAI MCP CAPABILITIES:
   - What services and tools are available?
   - What are the key strengths and features?
   
2. ANTHROPIC MCP CAPABILITIES:
   - What services and tools does Anthropic offer?
   - What are Claude's unique capabilities?

3. COMPARISON ANALYSIS:
   - How do their capabilities complement each other?
   - What would be interesting topics for them to discuss?

Provide a comprehensive capability assessment for both systems."""
    
    print("🤖 Router discovering MCP capabilities...")
    print("-" * 40)
    
    response, err = llm.Call(discovery_query, verbose=True)
    if err:
        print(f"❌ Error: {err}")
        return None
        
    print(f"✅ Capabilities Discovery:\n{response['content']}")
    
    tools_used = response.get('tool_calls_made', [])
    if tools_used:
        print(f"\n🔧 MCP Tools Used: {len(tools_used)}")
        for tool in tools_used:
            print(f"  - {tool['tool']}: {tool['input']}")
    
    return llm

def generate_conversation_questions(llm):
    """Step 2: Have OpenAI generate questions for Anthropic"""
    
    print("\n" + "=" * 60)
    print("❓ GENERATING CONVERSATION QUESTIONS")
    print("=" * 60)
    
    question_generation_query = """Now as the router, use the OpenAI MCP to generate 5-7 thoughtful questions that would create an engaging conversation with Anthropic's Claude.

The questions should:
1. Explore Anthropic's unique reasoning capabilities
2. Test Claude's analytical thinking
3. Invite philosophical or ethical discussions
4. Challenge problem-solving abilities
5. Explore creative thinking
6. Ask about AI capabilities and limitations

Use OpenAI to craft these questions specifically for meaningful AI-to-AI dialogue."""
    
    print("🤖 Router requesting OpenAI to generate questions...")
    print("-" * 40)
    
    response, err = llm.Call(question_generation_query, verbose=True)
    if err:
        print(f"❌ Error: {err}")
        return None
        
    print(f"✅ Generated Questions:\n{response['content']}")
    
    tools_used = response.get('tool_calls_made', [])
    if tools_used:
        print(f"\n🔧 OpenAI Tools Used: {len(tools_used)}")
        for tool in tools_used:
            print(f"  - {tool['tool']}: {tool['input']}")
    
    return response['content']

def route_questions_to_anthropic(llm, questions):
    """Step 3: Route questions to Anthropic MCP and collect responses"""
    
    print("\n" + "=" * 60)
    print("🎯 ROUTING QUESTIONS TO ANTHROPIC")
    print("=" * 60)
    
    routing_query = f"""As the conversation router, now take the questions that OpenAI generated and route them to the Anthropic MCP.

QUESTIONS FROM OPENAI:
{questions}

Please:
1. Send these questions one by one to Anthropic's Claude
2. Collect Claude's responses
3. Note any particularly interesting insights
4. Prepare a summary of the Q&A session

Route the conversation and collect Anthropic's responses."""
    
    print("🤖 Router sending questions to Anthropic...")
    print("-" * 40)
    
    response, err = llm.Call(routing_query, verbose=True)
    if err:
        print(f"❌ Error: {err}")
        return None
        
    print(f"✅ Anthropic's Responses:\n{response['content']}")
    
    tools_used = response.get('tool_calls_made', [])
    if tools_used:
        print(f"\n🔧 Anthropic Tools Used: {len(tools_used)}")
        for tool in tools_used:
            print(f"  - {tool['tool']}: {tool['input']}")
    
    return response['content']

def facilitate_follow_up_dialogue(llm, anthropic_responses):
    """Step 4: Facilitate follow-up dialogue between the systems"""
    
    print("\n" + "=" * 60)
    print("💬 FACILITATING FOLLOW-UP DIALOGUE")
    print("=" * 60)
    
    dialogue_query = f"""As the conversation router, now facilitate a follow-up dialogue:

ANTHROPIC'S RESPONSES:
{anthropic_responses}

Please:
1. Use OpenAI to analyze Anthropic's responses and generate follow-up questions
2. Route those follow-ups back to Anthropic
3. Create a meaningful back-and-forth exchange
4. Look for areas of agreement, disagreement, or complementary insights

Facilitate at least 2-3 rounds of back-and-forth dialogue between the systems."""
    
    print("🤖 Router facilitating dialogue...")
    print("-" * 40)
    
    response, err = llm.Call(dialogue_query, verbose=True)
    if err:
        print(f"❌ Error: {err}")
        return None
        
    print(f"✅ Follow-up Dialogue:\n{response['content']}")
    
    tools_used = response.get('tool_calls_made', [])
    if tools_used:
        print(f"\n🔧 Tools Used in Dialogue: {len(tools_used)}")
        for tool in tools_used:
            print(f"  - {tool['tool']}: {tool['input']}")
    
    return response['content']

def analyze_conversation_results(llm):
    """Step 5: Analyze the entire MCP-to-MCP conversation"""
    
    print("\n" + "=" * 60)
    print("📊 ANALYZING CONVERSATION RESULTS")
    print("=" * 60)
    
    analysis_query = """As the conversation router, provide a comprehensive analysis of the MCP-to-MCP conversation:

1. TECHNICAL ANALYSIS:
   - How well did the routing work?
   - Which MCP tools were most effective?
   - Any challenges in facilitating AI-to-AI communication?

2. CONVERSATION QUALITY:
   - What insights emerged from OpenAI-Anthropic dialogue?
   - Areas where they agreed or disagreed?
   - Unique perspectives each system brought?

3. ROUTING EFFECTIVENESS:
   - How successful was the router approach?
   - Benefits of having a mediating system?
   - Potential improvements?

4. PRACTICAL APPLICATIONS:
   - Real-world use cases for MCP-to-MCP communication?
   - How could this pattern be used in production?

Provide detailed analysis and recommendations."""
    
    print("🤖 Router analyzing conversation results...")
    print("-" * 40)
    
    response, err = llm.Call(analysis_query, verbose=False)
    if err:
        print(f"❌ Error: {err}")
        return
        
    print(f"✅ Conversation Analysis:\n{response['content']}")
    
    tools_used = response.get('tool_calls_made', [])
    if tools_used:
        print(f"\n🔧 Analysis Tools Used: {[tool['tool'] for tool in tools_used]}")

def main():
    """Main function to orchestrate MCP-to-MCP conversation"""
    
    print("🎭 MCP-TO-MCP CONVERSATION ORCHESTRATION")
    print("OpenAI MCP ↔️ Router ↔️ Anthropic MCP")
    print("=" * 70)
    
    try:
        print("🚀 Starting MCP-to-MCP conversation with router...")
        print("\nProcess:")
        print("1. 🔍 Discover capabilities of both MCPs")
        print("2. ❓ OpenAI generates questions for Anthropic")
        print("3. 🎯 Router sends questions to Anthropic")
        print("4. 💬 Facilitate follow-up dialogue")
        print("5. 📊 Analyze conversation results")
        print("=" * 50)
        
        # Step 1: Discover capabilities
        llm = discover_mcp_capabilities()
        if not llm:
            return
            
        input("\n⏸️ Press Enter to continue to question generation...")
        
        # Step 2: Generate questions
        questions = generate_conversation_questions(llm)
        if not questions:
            return
            
        input("\n⏸️ Press Enter to route questions to Anthropic...")
        
        # Step 3: Route to Anthropic
        anthropic_responses = route_questions_to_anthropic(llm, questions)
        if not anthropic_responses:
            return
            
        input("\n⏸️ Press Enter to facilitate follow-up dialogue...")
        
        # Step 4: Facilitate dialogue
        dialogue_results = facilitate_follow_up_dialogue(llm, anthropic_responses)
        if not dialogue_results:
            return
            
        input("\n⏸️ Press Enter for final analysis...")
        
        # Step 5: Analyze results
        analyze_conversation_results(llm)
        
        print("\n" + "=" * 70)
        print("🎉 MCP-TO-MCP CONVERSATION COMPLETE!")
        print("✅ Successfully orchestrated AI-to-AI communication")
        print("✅ OpenAI generated questions for Anthropic")
        print("✅ Router facilitated meaningful dialogue")
        print("✅ Comprehensive analysis provided")
        print("🔗 This demonstrates advanced MCP orchestration patterns!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ MCP conversation stopped by user")
    except Exception as e:
        print(f"❌ Error during MCP conversation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()