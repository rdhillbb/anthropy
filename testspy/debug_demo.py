#!/usr/bin/env python3
"""
Demonstration of Enhanced Debug Capabilities in anthrop.py
Shows comprehensive LLM message tracing for debugging purposes
"""

import os
from anthrop import CreateAnthropic, create_example_tools

def demo_basic_debug():
    """Demonstrate basic debug mode (boolean)"""
    print("=" * 70)
    print("🔍 DEMO 1: BASIC DEBUG MODE")
    print("=" * 70)
    
    config = {
        "model": "claude-sonnet-4-20250514",
        "tools": create_example_tools(),
        "debug": True,  # Simple boolean debug mode
        "system_prompt": "You are a helpful weather and news assistant."
    }
    
    llm, error = CreateAnthropic(config)
    if error:
        print(f"Error: {error}")
        return
    
    # Make a simple call
    response, error = llm.Call("Hello! Can you tell me about the weather in Tokyo?")
    if error:
        print(f"Error: {error}")
    else:
        print(f"Response received: {len(response['content'])} characters")

def demo_advanced_debug():
    """Demonstrate advanced debug configuration"""
    print("\n" + "=" * 70)
    print("🔍 DEMO 2: ADVANCED DEBUG CONFIGURATION")
    print("=" * 70)
    
    # Advanced debug configuration
    debug_config = {
        "enabled": True,
        "level": "full",
        "output": "console",
        "sections": {
            "system_prompt": True,
            "user_input": True,
            "message_buffer": True,
            "api_request": True,
            "api_response": True,
            "timing": True
        }
    }
    
    config = {
        "model": "claude-sonnet-4-20250514", 
        "tools": create_example_tools(),
        "debug": debug_config,  # Advanced debug configuration
        "system_prompt": "You are an expert analyst providing detailed weather and news information with citations."
    }
    
    llm, error = CreateAnthropic(config)
    if error:
        print(f"Error: {error}")
        return
    
    # Make multiple calls to show conversation history
    print("Making first call...")
    llm.Call("Hello, I'm starting a research session.")
    
    print("Making second call with tool usage...")
    llm.Call("What's the weather in New York and get me some technology news?")

def demo_selective_debug():
    """Demonstrate selective debug sections"""
    print("\n" + "=" * 70)
    print("🔍 DEMO 3: SELECTIVE DEBUG SECTIONS")
    print("=" * 70)
    
    # Only show API request and response, hide message buffer
    debug_config = {
        "enabled": True,
        "sections": {
            "system_prompt": False,
            "user_input": True,
            "message_buffer": False,  # Hide message buffer
            "api_request": True,
            "api_response": True,
            "timing": True
        }
    }
    
    config = {
        "model": "claude-sonnet-4-20250514",
        "tools": create_example_tools(), 
        "debug": debug_config,
        "system_prompt": "Provide concise and accurate information."
    }
    
    llm, error = CreateAnthropic(config)
    if error:
        print(f"Error: {error}")
        return
    
    # Build up some history first
    llm.Call("Remember my name is Alex.")
    llm.Call("What's my name and the weather in London?")

def demo_file_integration_debug():
    """Demonstrate debug with file attachments"""
    print("\n" + "=" * 70)
    print("🔍 DEMO 4: DEBUG WITH FILE ATTACHMENTS")
    print("=" * 70)
    
    config = {
        "model": "claude-sonnet-4-20250514",
        "tools": create_example_tools(),
        "debug": True,
        "system_prompt": "You are a document analysis assistant."
    }
    
    llm, error = CreateAnthropic(config)
    if error:
        print(f"Error: {error}")
        return
    
    # Create a temporary test file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Sample document content for debug testing.\nThis shows how file attachments appear in debug output.")
        test_file = f.name
    
    try:
        # Upload file
        print("Uploading test file...")
        file_id, error = llm.UploadFile(test_file, auto_attach=True)
        if error:
            print(f"File upload error: {error}")
            return
            
        print(f"File uploaded: {file_id}")
        
        # Make a call with file attachment
        llm.Call("Please analyze the uploaded document and provide a summary.")
        
        # Cleanup
        llm.DeleteFile(file_id)
        
    finally:
        os.unlink(test_file)

def main():
    """Run all debug demonstrations"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Please set ANTHROPIC_API_KEY environment variable")
        return
    
    print("🚀 ANTHROPIC API DEBUG CAPABILITIES DEMONSTRATION")
    print("This demo showcases comprehensive LLM message tracing")
    print()
    
    try:
        demo_basic_debug()
        demo_advanced_debug()
        demo_selective_debug() 
        demo_file_integration_debug()
        
        print("\n" + "=" * 70)
        print("✅ ALL DEBUG DEMONSTRATIONS COMPLETED")
        print("=" * 70)
        print()
        print("Key Features Demonstrated:")
        print("• 📋 System prompt visibility")
        print("• 💬 User input tracking")
        print("• 🗃️  Message buffer inspection")
        print("• 📤 API request details")
        print("• 📥 API response analysis")
        print("• ⏱️  Timing information")
        print("• 🎛️  Selective debug sections")
        print("• 📄 File attachment debugging")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")

if __name__ == "__main__":
    main()