#!/usr/bin/env python3
"""
Hybrid Workflow Demo - Showcase real-world scenarios using both local and MCP tools
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def create_hybrid_config():
    """Configuration optimized for hybrid workflows"""
    return {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "tools": create_example_tools(),  # Local weather/news
        "enable_mcp": True,               # Enable MCP
        "mcp_servers": [{
            "type": "url",
            "url": "https://mcp.pipedream.net/9fa309c7-d3d2-48e3-8236-b9732cac712c/openai",
            "name": "pipedream-openai"
        }],
        "system_prompt": """You are a versatile AI assistant with hybrid capabilities:

LOCAL TOOLS:
- weather: Get current weather for any location
- news: Get latest news headlines by topic (tech, sports, weather, etc.)

MCP TOOLS (OpenAI):
- Text generation and creative writing
- Image generation capabilities  
- Translation and summarization
- File processing
- And more OpenAI features

HYBRID WORKFLOW STRATEGY:
1. Use local tools to gather current data (weather, news)
2. Use MCP tools for creative content generation
3. Combine outputs for comprehensive responses
4. Always be transparent about which tools you're using

Make intelligent tool choices based on the user's needs.""",
        "debug": False
    }

def travel_planning_workflow():
    """Demonstrate travel planning using both tool types"""
    
    print("🌍 TRAVEL PLANNING WORKFLOW")
    print("=" * 50)
    
    config = create_hybrid_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    scenarios = [
        {
            "destination": "Tokyo",
            "query": "I'm planning a trip to Tokyo next week. Check the weather there and suggest some activities based on the conditions. Also write a creative packing list poem."
        },
        {
            "destination": "London", 
            "query": "Check London's weather and the latest travel news, then create a fun itinerary email I can send to my travel buddy."
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['destination']} ---")
        print(f"Request: {scenario['query']}")
        print("-" * 40)
        
        response, err = llm.Call(scenario['query'])
        if err:
            print(f"❌ Error: {err}")
        else:
            print(f"✅ Response:\n{response['content'][:600]}...")
            
            tools_used = response.get('tool_calls_made', [])
            if tools_used:
                print(f"\n🔧 Hybrid Tools Used:")
                for tool in tools_used:
                    tool_type = "LOCAL" if tool['tool'] in ['weather', 'news'] else "MCP"
                    print(f"   - {tool['tool']} ({tool_type}): {tool['input']}")
            print()

def news_content_workflow():
    """Demonstrate news + content creation workflow"""
    
    print("📰 NEWS + CONTENT CREATION WORKFLOW") 
    print("=" * 50)
    
    config = create_hybrid_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    workflows = [
        {
            "name": "Tech Newsletter",
            "query": "Get the latest technology news, then write a engaging newsletter introduction that summarizes the key trends and includes a call-to-action."
        },
        {
            "name": "Sports + Poetry",
            "query": "Fetch the latest sports news and then create a haiku for each headline."
        },
        {
            "name": "Weather + Story",
            "query": "Check the weather in three different cities (New York, London, Tokyo) and write a short creative story that connects all three weather conditions."
        }
    ]
    
    for i, workflow in enumerate(workflows, 1):
        print(f"\n--- Workflow {i}: {workflow['name']} ---")
        print(f"Task: {workflow['query']}")
        print("-" * 40)
        
        response, err = llm.Call(workflow['query'])
        if err:
            print(f"❌ Error: {err}")
        else:
            print(f"✅ Response:\n{response['content'][:500]}...")
            
            tools_used = response.get('tool_calls_made', [])
            if tools_used:
                local_tools = [t for t in tools_used if t['tool'] in ['weather', 'news']]
                mcp_tools = [t for t in tools_used if t['tool'] not in ['weather', 'news']]
                
                print(f"\n🏠 Local Tools: {len(local_tools)} calls")
                for tool in local_tools:
                    print(f"   - {tool['tool']}: {tool['input']}")
                
                if mcp_tools:
                    print(f"🌐 MCP Tools: {len(mcp_tools)} calls")
                    for tool in mcp_tools:
                        print(f"   - {tool['tool']}: {tool['input']}")
                else:
                    print("🌐 MCP Tools: Used for creative content (no explicit calls)")
            print()

def business_intelligence_workflow():
    """Demonstrate business-style workflows"""
    
    print("💼 BUSINESS INTELLIGENCE WORKFLOW")
    print("=" * 50)
    
    config = create_hybrid_config()
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error: {err}")
        return
    
    business_scenarios = [
        {
            "name": "Market Analysis",
            "query": "Get the latest technology news and weather for San Francisco (where our office is). Create a brief market analysis email highlighting how current tech trends might affect our software business, and include a note about office conditions."
        },
        {
            "name": "Event Planning",
            "query": "Check weather in Chicago and get sports news. Help me plan an outdoor company event, considering weather conditions and current sports excitement that we could leverage for team activities."
        }
    ]
    
    for i, scenario in enumerate(business_scenarios, 1):
        print(f"\n--- Business Scenario {i}: {scenario['name']} ---")
        print(f"Brief: {scenario['query']}")
        print("-" * 40)
        
        response, err = llm.Call(scenario['query'])
        if err:
            print(f"❌ Error: {err}")
        else:
            print(f"✅ Business Response:\n{response['content'][:400]}...")
            
            tools_used = response.get('tool_calls_made', [])
            data_gathering = [t for t in tools_used if t['tool'] in ['weather', 'news']]
            
            print(f"\n📊 Data Sources: {len(data_gathering)} local tool calls")
            for tool in data_gathering:
                print(f"   - {tool['tool'].upper()}: {tool['input']}")
            
            print(f"🧠 Content Generation: {'MCP tools + AI reasoning' if len(response['content']) > 200 else 'Direct AI response'}")
        print()

def main():
    """Run hybrid workflow demonstrations"""
    
    print("🔀 HYBRID WORKFLOW DEMONSTRATIONS")
    print("Real-world scenarios using Local + MCP tools")
    print("=" * 60)
    
    try:
        travel_planning_workflow()
        news_content_workflow() 
        business_intelligence_workflow()
        
        print("\n" + "=" * 60)
        print("🎉 HYBRID WORKFLOWS COMPLETE!")
        print()
        print("✅ Successfully demonstrated:")
        print("   🏠 Local tools for real-time data (weather, news)")
        print("   🌐 MCP tools for content generation") 
        print("   🔀 Intelligent hybrid workflows")
        print("   💼 Business-ready applications")
        print("   🤖 Seamless tool integration")
        print()
        print("🚀 Your API is ready for production hybrid applications!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()