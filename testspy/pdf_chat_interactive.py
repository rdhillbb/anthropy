#!/usr/bin/env python3
"""
Interactive PDF Chat Program
Uploads a PDF file and allows interactive Q&A with the document content
"""

import os
import sys
import argparse
from anthrop import CreateAnthropic, create_example_tools

class PDFChatSession:
    """Interactive PDF chat session manager"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.llm = None
        self.file_id = None
        self.session_active = False
        
    def initialize(self):
        """Initialize the LLM and upload the PDF"""
        print("🔧 Initializing PDF Chat Session...")
        
        # Check if PDF exists
        if not os.path.exists(self.pdf_path):
            print(f"❌ Error: PDF file not found: {self.pdf_path}")
            return False
        
        # Check API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("❌ Error: Please set ANTHROPIC_API_KEY environment variable")
            print("   Example: export ANTHROPIC_API_KEY='your-api-key-here'")
            return False
        
        # Create LLM instance
        config = {
            "model": "claude-sonnet-4-20250514",
            "tools": create_example_tools(),
            "max_tokens": 40000,
            "thinking_budget_tokens": 6000,
            "debug": False  # Set to True for debugging
        }
        
        self.llm, error = CreateAnthropic(config)
        if error:
            print(f"❌ Error creating LLM: {error}")
            return False
        
        print("✅ LLM initialized successfully")
        
        # Upload PDF file
        print(f"📄 Uploading PDF: {self.pdf_path}")
        self.file_id, error = self.llm.UploadFile(self.pdf_path, auto_attach=True)
        if error:
            print(f"❌ Error uploading PDF: {error}")
            return False
        
        print(f"✅ PDF uploaded successfully (File ID: {self.file_id})")
        
        # Test initial connection
        print("🧪 Testing document access...")
        response, error = self.llm.Call("Please confirm you can access the uploaded PDF and provide a brief description of what type of document this is.")
        
        if error:
            print(f"❌ Error testing document access: {error}")
            return False
        
        print("✅ Document access confirmed")
        print(f"📋 Document overview: {response['content'][:200]}...")
        print()
        
        self.session_active = True
        return True
    
    def cleanup(self):
        """Clean up uploaded files"""
        if self.file_id and self.llm:
            print("🧹 Cleaning up uploaded files...")
            success = self.llm.DeleteFile(self.file_id)
            if success:
                print("✅ File cleanup successful")
            else:
                print("⚠️  File cleanup failed (file may persist in your account)")
    
    def run_interactive_session(self):
        """Run the main interactive chat loop"""
        print("=" * 60)
        print("🎯 PDF CHAT INTERACTIVE SESSION STARTED")
        print("=" * 60)
        print(f"📄 Document: {os.path.basename(self.pdf_path)}")
        print()
        print("💬 You can now ask questions about the PDF content.")
        print("📝 Type 'help' for example questions")
        print("🚪 Type 'quit' or 'exit' to end the session")
        print("=" * 60)
        print()
        
        while self.session_active:
            try:
                # Get user input
                user_input = input("❓ Ask a question: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Ending session...")
                    break
                
                # Check for help command
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                # Check for status command
                if user_input.lower() == 'status':
                    self.show_status()
                    continue
                
                # Process the question
                print("🤔 Processing your question...")
                response, error = self.llm.Call(user_input, verbose=False)
                
                if error:
                    print(f"❌ Error processing question: {error}")
                    continue
                
                # Display response
                print()
                print("🤖 Response:")
                print("-" * 40)
                print(response['content'])
                print("-" * 40)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Session interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                continue
    
    def show_help(self):
        """Display help information"""
        print()
        print("📖 HELP - Example Questions You Can Ask:")
        print("-" * 40)
        print("• What is this document about?")
        print("• Summarize the key findings")
        print("• What are the main topics covered?")
        print("• Find information about [specific topic]")
        print("• What happened in [specific time period]?")
        print("• List the key recommendations")
        print("• What are the financial highlights?")
        print("• Who are the key people mentioned?")
        print()
        print("📋 Special Commands:")
        print("• 'help' - Show this help message")
        print("• 'status' - Show session information")
        print("• 'quit' or 'exit' - End the session")
        print("-" * 40)
        print()
    
    def show_status(self):
        """Display session status"""
        print()
        print("📊 SESSION STATUS:")
        print("-" * 30)
        print(f"📄 Document: {os.path.basename(self.pdf_path)}")
        print(f"🆔 File ID: {self.file_id}")
        print(f"💬 Conversation History: {len(self.llm.GetHistory())} messages")
        
        # Show file info
        files = self.llm.ListFiles()
        our_file = next((f for f in files if f["id"] == self.file_id), None)
        if our_file:
            print(f"📏 File Size: {our_file['size']:,} bytes")
            print(f"📅 Upload Time: {our_file['created_at']}")
        
        print("-" * 30)
        print()

def main():
    """Main program entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Interactive PDF Chat Program")
    parser.add_argument("-f", "--file", 
                       type=str, 
                       default="2024-Tradewinds-Year-in-Review.pdf",
                       help="PDF file to analyze (default: 2024-Tradewinds-Year-in-Review.pdf)")
    
    args = parser.parse_args()
    
    # Determine PDF path
    if os.path.isabs(args.file):
        pdf_path = args.file  # Absolute path provided
    else:
        pdf_path = os.path.join(os.getcwd(), args.file)  # Relative to current directory
    
    print("🔍 PDF Interactive Chat Program")
    print("=" * 50)
    print(f"📄 Target file: {args.file}")
    
    # Initialize session
    session = PDFChatSession(pdf_path)
    
    try:
        # Initialize LLM and upload PDF
        if not session.initialize():
            print("❌ Failed to initialize session")
            sys.exit(1)
        
        # Run interactive chat
        session.run_interactive_session()
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
    
    finally:
        # Cleanup
        session.cleanup()
        print("✅ Session ended successfully")

if __name__ == "__main__":
    main()