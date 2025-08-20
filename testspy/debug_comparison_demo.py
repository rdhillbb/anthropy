#!/usr/bin/env python3
"""
Debug Comparison Demo
Runs the same application twice - once with debug, once without
"""

import os
import sys
import subprocess
import time

def run_application(debug_mode=False, output_file=None):
    """Run the weather news application with or without debug"""
    cmd = ["python3", "weather_news_app.py"]
    if debug_mode:
        cmd.append("--debug")
    
    try:
        if output_file:
            with open(output_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, 
                                     text=True, timeout=120)
            return result.returncode == 0
        else:
            result = subprocess.run(cmd, timeout=120)
            return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Application timed out")
        return False
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return False

def main():
    """Main demonstration script"""
    print("🔍 DEBUG COMPARISON DEMONSTRATION")
    print("=" * 60)
    print("This demo runs the same application twice:")
    print("1. 🔇 Clean mode (debug disabled)")
    print("2. 🔍 Debug mode (debug enabled)")
    print("=" * 60)
    
    # Check prerequisites
    if not os.path.exists("weather_news_app.py"):
        print("❌ Error: weather_news_app.py not found")
        return 1
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: Please set ANTHROPIC_API_KEY environment variable")
        return 1
    
    print("\n🎯 OPTION 1: Side-by-side comparison (save outputs to files)")
    print("🎯 OPTION 2: Sequential runs (live console output)")
    choice = input("\nChoose option (1 or 2): ").strip()
    
    if choice == "1":
        return run_side_by_side_comparison()
    elif choice == "2":
        return run_sequential_demonstration()
    else:
        print("❌ Invalid choice")
        return 1

def run_side_by_side_comparison():
    """Run both versions and save outputs to files for comparison"""
    print("\n🔄 Running side-by-side comparison...")
    print("📝 Outputs will be saved to files for comparison")
    
    # Run clean version
    print("\n1️⃣ Running CLEAN version...")
    clean_success = run_application(debug_mode=False, output_file="output_clean.txt")
    
    if clean_success:
        print("✅ Clean version completed - output saved to 'output_clean.txt'")
    else:
        print("❌ Clean version failed")
        return 1
    
    # Small delay
    time.sleep(2)
    
    # Run debug version  
    print("\n2️⃣ Running DEBUG version...")
    debug_success = run_application(debug_mode=True, output_file="output_debug.txt")
    
    if debug_success:
        print("✅ Debug version completed - output saved to 'output_debug.txt'")
    else:
        print("❌ Debug version failed")
        return 1
    
    # Show comparison summary
    print("\n" + "=" * 60)
    print("📊 COMPARISON SUMMARY")
    print("=" * 60)
    
    # Get file sizes
    try:
        clean_size = os.path.getsize("output_clean.txt")
        debug_size = os.path.getsize("output_debug.txt")
        
        print(f"📄 Clean output size: {clean_size:,} bytes")
        print(f"📄 Debug output size: {debug_size:,} bytes") 
        print(f"📈 Debug output is {debug_size/clean_size:.1f}x larger")
        
        # Count lines
        with open("output_clean.txt", 'r') as f:
            clean_lines = len(f.readlines())
        with open("output_debug.txt", 'r') as f:
            debug_lines = len(f.readlines())
        
        print(f"📝 Clean output lines: {clean_lines}")
        print(f"📝 Debug output lines: {debug_lines}")
        print(f"📈 Debug output has {debug_lines - clean_lines} additional lines")
        
    except Exception as e:
        print(f"⚠️ Could not analyze file sizes: {e}")
    
    print("\n🔍 TO COMPARE OUTPUTS:")
    print("• View clean version: cat output_clean.txt")
    print("• View debug version: cat output_debug.txt") 
    print("• Compare side-by-side: diff -u output_clean.txt output_debug.txt")
    print("• Or use your preferred diff tool")
    
    return 0

def run_sequential_demonstration():
    """Run both versions sequentially with live console output"""
    print("\n🔄 Running sequential demonstration...")
    
    # Run clean version
    print("\n" + "🔇" * 20)
    print("1️⃣ CLEAN VERSION (Debug Disabled)")
    print("🔇" * 20)
    input("Press Enter to start clean version...")
    
    clean_success = run_application(debug_mode=False)
    
    if not clean_success:
        print("❌ Clean version failed")
        return 1
    
    print("\n✅ Clean version completed!")
    input("\nPress Enter to continue to debug version...")
    
    # Run debug version
    print("\n" + "🔍" * 20) 
    print("2️⃣ DEBUG VERSION (Debug Enabled)")
    print("🔍" * 20)
    print("⚠️ Note: This will show much more detailed output!")
    input("Press Enter to start debug version...")
    
    debug_success = run_application(debug_mode=True)
    
    if not debug_success:
        print("❌ Debug version failed") 
        return 1
    
    print("\n✅ Debug version completed!")
    
    print("\n" + "=" * 60)
    print("🎯 DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("Key Differences Observed:")
    print("🔇 Clean Version:")
    print("  • Minimal, user-friendly output")
    print("  • Only essential information shown")
    print("  • Production-ready appearance")
    print()
    print("🔍 Debug Version:")
    print("  • Comprehensive API tracing")
    print("  • System prompt visibility")
    print("  • Message buffer inspection")
    print("  • Timing and performance data")
    print("  • Tool execution details")
    
    return 0

if __name__ == "__main__":
    exit(main())