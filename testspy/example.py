#!/usr/bin/env python3
"""
Example program demonstrating the anthrop.py API
"""

import sys
from anthrop import CreateAnthropic, create_example_tools

def create_system_prompt():
    """Create the system prompt for the examples"""
    return """You are a helpful conversational assistant.

Provide complete, informative responses while being natural and engaging. When users ask questions:
- Use your tools when appropriate to get current information
- Give thorough answers that fully address the user's needs
- Be conversational but professional
- Provide context and helpful details when relevant
- If you can't fulfill part of a request, explain what you can do instead
- For complex requests, organize your response clearly

Always respond fully with requests.
Your goal is to be genuinely helpful while maintaining a natural conversational flow."""

def run_examples():
    """Run the five example scenarios demonstrating the API"""
    
    # Create LLM object with configurable system prompt
    config = {
        "model": "claude-sonnet-4-20250514",
        "tools": create_example_tools(),
        "temperature": 0.6,
        "system_prompt": create_system_prompt(),
        "debug": False 
    }
    
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error creating LLM: {err}")
        sys.exit(1)
    
    # Example 1: Basic single tool call
    print("=== Example 1: Basic Weather Query ===")
    response, err = llm.Call("What's the weather in London?")
    if err:
        print(f"Error: {err}")
    else:
        print(f"Response: {response['content']}")
    
    # Example 2: Compound query with multiple tools
    print("\n=== Example 2: Compound Query ===")
    response, err = llm.Call("What's the weather in Paris and what's the latest tech news?")
    if err:
        print(f"Error: {err}")
    else:
        print(f"Response: {response['content']}")
    
    # Example 3: Complex multi-part request
    print("\n=== Example 3: Complex Multi-Part Request ===")
    response, err = llm.Call("Be creative about the weather, provide a report on Katherine Johnson. Check the where of her home town. Write a short repprot on Johns hopkins. Compare the report of Katherine. also what is the wather in London")
    if err:
        print(f"Error: {err}")
    else:
        print(f"Response: {response['content']}")
        
    # Example 4: Conversation summary
    print("\n=== Example 4: Conversation Summary ===")
    response, err = llm.Call("Please give me a recap of our conversatioin. Include each request made and the full details of the response to each request.")
    if err:
        print(f"Error: {err}")
    else:
        print(f"Response: {response['content']}")
        
    # Example 5: Simple conversational response
    print("\n=== Example 5: Simple Thank You ===")
    response, err = llm.Call("Thank you")
    if err:
        print(f"Error: {err}")
    else:
        print(f"Response: {response['content']}")

def run_custom_example():
    """Demonstrate how to use the API with a custom system prompt"""
    
    print("\n" + "="*60)
    print("=== Custom System Prompt Example ===")
    print("="*60)
    
    # Create a different system prompt for demonstration
    custom_prompt = """You are a formal, scientific assistant specializing in weather and news data.
Provide concise, technical responses with minimal conversational elements.
Focus on data accuracy and scientific terminology when appropriate."""
    
    config = {
        "model": "claude-sonnet-4-20250514", 
        "tools": create_example_tools(),
        "temperature": 0.3,  # Lower temperature for more formal responses
        "system_prompt": custom_prompt,
        "debug": False
    }
    
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error creating LLM: {err}")
        return
    
    print("Using formal/scientific system prompt...")
    response, err = llm.Call("What's the weather in London?")
    if err:
        print(f"Error: {err}")
    else:
        print(f"Response: {response['content']}")

def demonstrate_verbose_mode():
    """Demonstrate the verbose flag functionality"""
    
    print("\n" + "="*60)
    print("=== Verbose Mode Demonstration ===")
    print("="*60)
    
    config = {
        "model": "claude-sonnet-4-20250514",
        "tools": create_example_tools(), 
        "temperature": 0.6,
        "system_prompt": create_system_prompt(),
        "debug": False
    }
    
    llm, err = CreateAnthropic(config)
    if err:
        print(f"Error creating LLM: {err}")
        return
    
    print("=== With verbose=True (shows debug output) ===")
    response, err = llm.Call("What's the weather in Paris?", verbose=True)
    if err:
        print(f"Error: {err}")
    else:
        print(f"Final Response: {response['content']}")
    
    print("\n=== With verbose=False (clean output) ===")
    response, err = llm.Call("What's the latest tech news?", verbose=False)
    if err:
        print(f"Error: {err}")
    else:
        print(f"Response: {response['content']}")

def main():
    """Main function to run all examples"""
    
    print("Anthropic API Example Demonstrations")
    print("="*50)
    print("This program demonstrates the anthrop.py API capabilities:")
    print("- Tool usage (weather and news)")
    print("- System prompt configuration") 
    print("- Multiple conversation scenarios")
    print("- Verbose mode options")
    print("="*50)
    
    try:
        # Run the main examples
        run_examples()
        
        # Show custom system prompt usage
        run_custom_example()
        
        # Demonstrate verbose mode
        demonstrate_verbose_mode()
        
        print("\n" + "="*50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
