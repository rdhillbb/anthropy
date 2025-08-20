#!/usr/bin/env python3
"""
Weather and News Application
Sample application to demonstrate debug capabilities
Usage: python3 weather_news_app.py [--debug]
"""

import os
import argparse
from anthrop import CreateAnthropic, create_example_tools

class WeatherNewsApp:
    """Simple weather and news application"""
    
    def __init__(self, debug_enabled=False):
        """Initialize the application with optional debug mode"""
        self.debug_enabled = debug_enabled
        self.llm = None
        self.session_active = False
        
    def initialize(self):
        """Initialize the LLM with appropriate debug settings"""
        print("🌤️ Weather & News App Initializing...")
        
        # Check API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("❌ Error: Please set ANTHROPIC_API_KEY environment variable")
            return False
        
        # Configure debug settings
        if self.debug_enabled:
            debug_config = {
                "enabled": True,
                "level": "full",
                "sections": {
                    "system_prompt": True,
                    "user_input": True, 
                    "message_buffer": True,
                    "api_request": True,
                    "api_response": True,
                    "timing": True
                }
            }
            print("🔍 Debug mode: ENABLED - Full debug tracing active")
        else:
            debug_config = False
            print("🔇 Debug mode: DISABLED - Clean output mode")
        
        # Create LLM configuration
        config = {
            "model": "claude-sonnet-4-20250514",
            "tools": create_example_tools(),
            "max_tokens": 40000,
            "thinking_budget_tokens": 6000,
            "debug": debug_config,
            "system_prompt": "You are a helpful weather and news assistant. Provide accurate, concise information and use available tools when appropriate."
        }
        
        # Initialize LLM
        self.llm, error = CreateAnthropic(config)
        if error:
            print(f"❌ Error creating LLM: {error}")
            return False
        
        print("✅ Application initialized successfully")
        return True
    
    def run_sample_workflow(self):
        """Execute a sample workflow to demonstrate the application"""
        print("\n" + "=" * 50)
        print("🚀 STARTING SAMPLE WORKFLOW")
        print("=" * 50)
        
        # Step 1: Welcome message
        print("\n📝 Step 1: Welcome interaction")
        print("-" * 30)
        response, error = self.llm.Call("Hello! I'm starting a weather and news session.")
        if error:
            print(f"❌ Error: {error}")
            return False
        print(f"🤖 Response: {response['content'][:100]}...")
        
        # Step 2: Weather query
        print("\n🌤️ Step 2: Weather information request")
        print("-" * 30)
        response, error = self.llm.Call("What's the weather like in Tokyo today?")
        if error:
            print(f"❌ Error: {error}")
            return False
        print(f"🤖 Response: {response['content'][:150]}...")
        
        # Step 3: News query
        print("\n📰 Step 3: Technology news request")
        print("-" * 30)
        response, error = self.llm.Call("Can you get me the latest technology news?")
        if error:
            print(f"❌ Error: {error}")
            return False
        print(f"🤖 Response: {response['content'][:150]}...")
        
        # Step 4: Combined query (should use conversation history)
        print("\n🔄 Step 4: Follow-up question using conversation history")
        print("-" * 30)
        response, error = self.llm.Call("Based on our conversation, what was the weather in Tokyo and give me one more tech headline?")
        if error:
            print(f"❌ Error: {error}")
            return False
        print(f"🤖 Response: {response['content'][:200]}...")
        
        # Step 5: Conversation summary
        print("\n📋 Step 5: Session summary")
        print("-" * 30)
        response, error = self.llm.Call("Please summarize what we discussed in this session.")
        if error:
            print(f"❌ Error: {error}")
            return False
        print(f"🤖 Response: {response['content'][:200]}...")
        
        return True
    
    def show_session_stats(self):
        """Display session statistics"""
        print("\n" + "=" * 50)
        print("📊 SESSION STATISTICS")
        print("=" * 50)
        
        history = self.llm.GetHistory()
        print(f"💬 Total messages in conversation: {len(history)}")
        print(f"🔍 Debug mode was: {'ENABLED' if self.debug_enabled else 'DISABLED'}")
        print(f"🤖 Application completed successfully")
        
        if self.debug_enabled:
            print("\n🔍 DEBUG MODE NOTES:")
            print("• Full API request/response tracing was shown")
            print("• System prompt visibility enabled")
            print("• Message buffer inspection active") 
            print("• Timing information provided")
            print("• Tool execution details displayed")
        else:
            print("\n🔇 CLEAN MODE NOTES:")
            print("• Only essential application output shown")
            print("• No debug tracing displayed")
            print("• Streamlined user experience")
            print("• Production-ready output format")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Weather and News Application - Debug Demonstration")
    parser.add_argument("--debug", action="store_true", help="Enable comprehensive debug output")
    
    args = parser.parse_args()
    
    print("🌤️ WEATHER & NEWS APPLICATION")
    print("=" * 50)
    print("Sample application demonstrating debug capabilities")
    
    if args.debug:
        print("🔍 Running in DEBUG MODE - Full tracing enabled")
    else:
        print("🔇 Running in CLEAN MODE - Production output")
    
    print("=" * 50)
    
    # Initialize application
    app = WeatherNewsApp(debug_enabled=args.debug)
    
    try:
        if not app.initialize():
            print("❌ Application initialization failed")
            return 1
        
        # Run the sample workflow
        if not app.run_sample_workflow():
            print("❌ Sample workflow failed")
            return 1
        
        # Show statistics
        app.show_session_stats()
        
        print("\n✅ Application completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())