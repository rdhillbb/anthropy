#!/usr/bin/env python3
"""
Test file upload integration for AnthropicLLM
"""

import os
import tempfile
import argparse
from anthrop import CreateAnthropic, create_example_tools

def create_test_file(content="This is a test file for file upload functionality."):
    """Create a temporary test file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        return f.name

def test_file_upload_system(test_file_path=None):
    """Test the complete file upload system."""
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Please set ANTHROPIC_API_KEY environment variable")
        return False
    
    # Create LLM instance
    config = {
        "model": "claude-sonnet-4-20250514",
        "tools": create_example_tools(),
        "max_tokens": 40000,
        "thinking_budget_tokens": 6000,
        "debug": True
    }
    
    llm, error = CreateAnthropic(config)
    if error:
        print(f"ERROR creating LLM: {error}")
        return False
    
    print("✓ LLM created successfully")
    
    # Use provided file or create test file
    if test_file_path:
        if not os.path.exists(test_file_path):
            print(f"ERROR: File not found: {test_file_path}")
            return False
        print(f"✓ Using provided file: {test_file_path}")
        cleanup_file = False
    else:
        test_file_path = create_test_file("Test content for file upload validation.")
        print(f"✓ Test file created: {test_file_path}")
        cleanup_file = True
    
    try:
        # Test 1: Upload file
        print("\n--- Test 1: File Upload ---")
        file_id, error = llm.UploadFile(test_file_path, auto_attach=True)
        if error:
            print(f"✗ File upload failed: {error}")
            return False
        
        print(f"✓ File uploaded successfully: {file_id}")
        
        # Test 2: List files
        print("\n--- Test 2: List Files ---")
        files = llm.ListFiles()
        print(f"✓ Found {len(files)} files")
        
        # Find our uploaded file
        our_file = None
        for f in files:
            if f["id"] == file_id:
                our_file = f
                break
        
        if not our_file:
            print("✗ Uploaded file not found in file list")
            return False
        
        print(f"✓ File found in list: {our_file['name']} ({our_file['size']} bytes)")
        
        # Test 3: Conversation with file attachment
        print("\n--- Test 3: Conversation with File ---")
        response, error = llm.Call(
            "Please summarize the content of the uploaded file.", 
            verbose=True
        )
        
        if error:
            print(f"✗ Conversation with file failed: {error}")
            return False
            
        print(f"✓ Conversation successful")
        print(f"Response: {response['content']}")
        
        # Test 4: File deletion
        print("\n--- Test 4: File Deletion ---")
        success = llm.DeleteFile(file_id)
        if not success:
            print("✗ File deletion failed")
            return False
            
        print("✓ File deleted successfully")
        
        # Verify deletion
        files_after = llm.ListFiles()
        file_still_exists = any(f["id"] == file_id for f in files_after)
        if file_still_exists:
            print("✗ File still exists after deletion")
            return False
            
        print("✓ File deletion verified")
        
        return True
        
    finally:
        # Clean up test file only if we created it
        if cleanup_file:
            try:
                os.unlink(test_file_path)
                print(f"✓ Test file cleaned up: {test_file_path}")
            except:
                print(f"⚠ Could not clean up test file: {test_file_path}")

def main():
    parser = argparse.ArgumentParser(description="Test file upload integration for AnthropicLLM")
    parser.add_argument("-f", "--file", type=str, help="Path to file to upload for testing")
    args = parser.parse_args()
    
    print("Testing File Upload Integration for AnthropicLLM")
    print("=" * 50)
    
    if args.file:
        print(f"Using file: {args.file}")
    else:
        print("Using auto-generated test file")
    
    success = test_file_upload_system(args.file)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ALL TESTS PASSED - File upload system working correctly!")
    else:
        print("❌ TESTS FAILED - File upload system needs fixes")
        exit(1)

if __name__ == "__main__":
    main()