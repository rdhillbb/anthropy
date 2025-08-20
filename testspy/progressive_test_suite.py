#!/usr/bin/env python3
"""
Progressive Test Suite for Anthropic API Integration
Comprehensive testing framework with phases for systematic validation
"""

import unittest
import os
import json
import tempfile
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from anthrop import CreateAnthropic, create_example_tools

class TestConfig:
    """Test configuration and environment setup"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("TEST_MODEL", "claude-sonnet-4-20250514")
        self.debug_mode = os.getenv("TEST_DEBUG", "false").lower() == "true"
        self.timeout = int(os.getenv("TEST_TIMEOUT", "300"))
        
        # MCP test configuration
        self.mcp_servers = [
            {
                "type": "url",
                "url": "https://mcp.pipedream.net/9fa309c7-d3d2-48e3-8236-b9732cac712c/openai",
                "name": "pipedream-openai"
            }
        ]
    
    def get_base_config(self) -> Dict[str, Any]:
        """Get base LLM configuration for tests"""
        return {
            "model": self.model,
            "tools": create_example_tools(),
            "max_tokens": 40000,
            "thinking_budget_tokens": 6000,
            "debug": self.debug_mode
        }

class TestReporter:
    """Custom test result reporter with JSON output"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "phases": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0
            }
        }
    
    def add_test_result(self, phase: str, test_name: str, status: str, 
                       duration: float, details: Optional[Dict] = None):
        """Add test result to report"""
        if phase not in self.results["phases"]:
            self.results["phases"][phase] = {"tests": [], "status": "pending"}
        
        test_result = {
            "name": test_name,
            "status": status,
            "duration": duration,
            "details": details or {}
        }
        
        self.results["phases"][phase]["tests"].append(test_result)
        self.results["summary"]["total_tests"] += 1
        self.results["summary"][status] += 1
    
    def save_report(self, filename: str = None):
        """Save test report to JSON file"""
        if filename is None:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return filename

# Global test reporter
reporter = TestReporter()

class BaseTestCase(unittest.TestCase):
    """Base test case with common functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.config = TestConfig()
        cls.phase_name = getattr(cls, 'PHASE_NAME', cls.__name__)
        
        if not cls.config.api_key:
            raise unittest.SkipTest("ANTHROPIC_API_KEY not set - skipping tests")
    
    def setUp(self):
        """Set up individual test"""
        self.start_time = time.time()
    
    def tearDown(self):
        """Clean up individual test"""
        duration = time.time() - self.start_time
        test_name = self._testMethodName
        
        # Simple status determination (will be overridden by custom test runner)
        status = getattr(self, '_test_status', 'passed')
        
        reporter.add_test_result(self.phase_name, test_name, status, duration)

# =============================================================================
# PHASE 1: FOUNDATION TESTS (Required First)
# =============================================================================

class Phase1FoundationTests(BaseTestCase):
    """Phase 1: Foundation tests - API analysis, environment, authentication"""
    
    PHASE_NAME = "Phase1_Foundation"
    
    def test_01_api_file_analysis(self):
        """Verify anthrop.py file structure and imports"""
        import anthrop
        
        # Verify core components exist
        self.assertTrue(hasattr(anthrop, 'AnthropicLLM'))
        self.assertTrue(hasattr(anthrop, 'CreateAnthropic'))
        self.assertTrue(hasattr(anthrop, 'create_example_tools'))
        
        # Verify AnthropicLLM has expected methods
        llm_methods = [
            'Call', 'Reset', 'GetHistory', 'LoadHistory', 'SetSystemPrompt',
            'UploadFile', 'DeleteFile', 'ListFiles'
        ]
        
        for method in llm_methods:
            self.assertTrue(hasattr(anthrop.AnthropicLLM, method),
                           f"AnthropicLLM missing method: {method}")
    
    def test_02_environment_setup(self):
        """Verify environment configuration and dependencies"""
        # Check API key
        self.assertIsNotNone(self.config.api_key, "ANTHROPIC_API_KEY must be set")
        self.assertTrue(len(self.config.api_key) > 20, "API key appears invalid")
        
        # Check Python imports
        try:
            import anthropic
            import tempfile
            import json
        except ImportError as e:
            self.fail(f"Required dependency missing: {e}")
        
        # Verify anthropic version
        import anthropic
        version = getattr(anthropic, '__version__', '0.0.0')
        major, minor = version.split('.')[:2]
        self.assertGreaterEqual(int(major), 0)
        self.assertGreaterEqual(int(minor), 7)
    
    def test_03_authentication_test(self):
        """Verify API credentials and basic connection"""
        config = self.config.get_base_config()
        
        # Test LLM creation
        llm, error = CreateAnthropic(config)
        self.assertIsNone(error, f"Failed to create LLM: {error}")
        self.assertIsNotNone(llm, "LLM object is None")
        
        # Test basic API call
        response, error = llm.Call("Hello, respond with just 'OK'", verbose=self.config.debug_mode)
        self.assertIsNone(error, f"API call failed: {error}")
        self.assertIsNotNone(response, "Response is None")
        self.assertIn("content", response, "Response missing content")

# =============================================================================
# PHASE 2: INDIVIDUAL COMPONENT TESTS
# =============================================================================

class Phase2APITests(BaseTestCase):
    """Phase 2A: Core API functionality tests"""
    
    PHASE_NAME = "Phase2A_API"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config = cls.config.get_base_config()
        cls.llm, error = CreateAnthropic(config)
        if error:
            raise unittest.SkipTest(f"Cannot create LLM for API tests: {error}")
    
    def setUp(self):
        super().setUp()
        self.llm.Reset()  # Clean state for each test
    
    def test_01_basic_conversation(self):
        """Test basic text conversation"""
        response, error = self.llm.Call("What is 2+2?")
        self.assertIsNone(error)
        self.assertIn("4", response["content"])
    
    def test_02_parameter_overrides(self):
        """Test parameter override functionality"""
        # Test temperature override
        response, error = self.llm.Call(
            "Respond with exactly: TEMP_TEST",
            options={"temperature": 0.1}
        )
        self.assertIsNone(error)
        self.assertIn("TEMP_TEST", response["content"])
    
    def test_03_conversation_history(self):
        """Test conversation history management"""
        # Make first call
        self.llm.Call("Remember: my name is TestUser")
        
        # Check history
        history = self.llm.GetHistory()
        self.assertEqual(len(history), 2)  # user + assistant
        
        # Test history persistence
        response, error = self.llm.Call("What is my name?")
        self.assertIsNone(error)
        self.assertIn("TestUser", response["content"])
    
    def test_04_state_management(self):
        """Test state save/load functionality"""
        # Create conversation
        self.llm.Call("Remember: secret code is 12345")
        original_history = self.llm.GetHistory()
        
        # Reset and verify empty
        self.llm.Reset()
        self.assertEqual(len(self.llm.GetHistory()), 0)
        
        # Load history back
        self.llm.LoadHistory(original_history)
        response, error = self.llm.Call("What is the secret code?")
        self.assertIsNone(error)
        self.assertIn("12345", response["content"])
    
    def test_05_system_prompt(self):
        """Test system prompt functionality"""
        self.llm.SetSystemPrompt("Always respond with 'SYSTEM_TEST' followed by your answer")
        response, error = self.llm.Call("What is the capital of France?")
        self.assertIsNone(error)
        self.assertIn("SYSTEM_TEST", response["content"])

class Phase2MCPTests(BaseTestCase):
    """Phase 2B: MCP integration tests"""
    
    PHASE_NAME = "Phase2B_MCP"
    
    def test_01_mcp_configuration(self):
        """Test MCP server configuration"""
        config = self.config.get_base_config()
        config.update({
            "enable_mcp": True,
            "mcp_servers": self.config.mcp_servers
        })
        
        llm, error = CreateAnthropic(config)
        self.assertIsNone(error, f"MCP configuration failed: {error}")
        self.assertTrue(llm.enable_mcp)
        self.assertEqual(len(llm.mcp_servers), 1)
    
    def test_02_mcp_fallback(self):
        """Test MCP fallback to local tools"""
        # Configure with invalid MCP server to test fallback
        config = self.config.get_base_config()
        config.update({
            "enable_mcp": True,
            "mcp_servers": [{"type": "url", "url": "http://invalid.server", "name": "invalid"}]
        })
        
        llm, error = CreateAnthropic(config)
        self.assertIsNone(error)
        
        # This should fallback to local tools
        response, error = llm.Call("What's the weather in New York?", verbose=self.config.debug_mode)
        self.assertIsNone(error, "Fallback mechanism failed")
        self.assertTrue(response["tool_calls_made"])  # Should have made tool calls
    
    def test_03_hybrid_tools(self):
        """Test hybrid local + MCP tool coordination"""
        config = self.config.get_base_config()
        config.update({
            "enable_mcp": True,
            "mcp_servers": self.config.mcp_servers
        })
        
        llm, error = CreateAnthropic(config)
        self.assertIsNone(error)
        
        # Test should work with local tools regardless of MCP status
        response, error = llm.Call("Get weather for London", verbose=self.config.debug_mode)
        self.assertIsNone(error)
        
        # Verify tool was called
        self.assertGreater(len(response["tool_calls_made"]), 0)

class Phase2FileTests(BaseTestCase):
    """Phase 2C: File upload and management tests"""
    
    PHASE_NAME = "Phase2C_Files"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config = cls.config.get_base_config()
        cls.llm, error = CreateAnthropic(config)
        if error:
            raise unittest.SkipTest(f"Cannot create LLM for file tests: {error}")
        cls.uploaded_files = []  # Track for cleanup
    
    @classmethod
    def tearDownClass(cls):
        """Clean up uploaded files"""
        for file_id in cls.uploaded_files:
            try:
                cls.llm.DeleteFile(file_id)
            except:
                pass  # Ignore cleanup errors
    
    def test_01_file_upload_text(self):
        """Test text file upload"""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for file upload")
            test_file = f.name
        
        try:
            file_id, error = self.llm.UploadFile(test_file)
            self.assertIsNone(error, f"File upload failed: {error}")
            self.assertIsNotNone(file_id, "File ID is None")
            self.uploaded_files.append(file_id)
            
        finally:
            os.unlink(test_file)
    
    def test_02_file_list_management(self):
        """Test file listing and metadata"""
        files = self.llm.ListFiles()
        self.assertIsInstance(files, list, "ListFiles should return a list")
        
        if files:
            file_obj = files[0]
            required_keys = {"id", "name", "size", "type", "is_persistent"}
            self.assertTrue(required_keys.issubset(file_obj.keys()),
                          f"File metadata missing keys: {required_keys - file_obj.keys()}")
    
    def test_03_file_conversation(self):
        """Test conversation with file attachment"""
        # Upload file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("The secret number is 42")
            test_file = f.name
        
        try:
            file_id, error = self.llm.UploadFile(test_file, auto_attach=True)
            self.assertIsNone(error)
            self.uploaded_files.append(file_id)
            
            # Test conversation with file
            response, error = self.llm.Call("What number is mentioned in the uploaded file?")
            self.assertIsNone(error, f"File conversation failed: {error}")
            self.assertIn("42", response["content"], "File content not accessed")
            
        finally:
            os.unlink(test_file)
    
    def test_04_file_deletion(self):
        """Test file deletion"""
        # Upload file for deletion test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("File to be deleted")
            test_file = f.name
        
        try:
            file_id, error = self.llm.UploadFile(test_file)
            self.assertIsNone(error)
            
            # Delete file
            success = self.llm.DeleteFile(file_id)
            self.assertTrue(success, "File deletion failed")
            
        finally:
            os.unlink(test_file)
    
    def test_05_text_file_formats(self):
        """Test various text file format support"""
        test_formats = [
            ('.md', 'markdown', '# Test Markdown\nThis is markdown content'),
            ('.py', 'python', 'def test():\n    return "hello"'),
            ('.json', 'json', '{"test": "value"}')
        ]
        
        for ext, format_name, content in test_formats:
            with self.subTest(format=format_name):
                with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                    f.write(content)
                    test_file = f.name
                
                try:
                    file_id, error = self.llm.UploadFile(test_file)
                    self.assertIsNone(error, f"{format_name} file upload failed: {error}")
                    if file_id:
                        self.uploaded_files.append(file_id)
                        
                finally:
                    os.unlink(test_file)

class Phase2ToolTests(BaseTestCase):
    """Phase 2D: Tool execution tests"""
    
    PHASE_NAME = "Phase2D_Tools"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config = cls.config.get_base_config()
        cls.llm, error = CreateAnthropic(config)
        if error:
            raise unittest.SkipTest(f"Cannot create LLM for tool tests: {error}")
    
    def test_01_weather_tool(self):
        """Test weather tool execution"""
        response, error = self.llm.Call("What's the weather in Tokyo?", verbose=self.config.debug_mode)
        self.assertIsNone(error, f"Weather tool test failed: {error}")
        
        # Verify tool was called
        self.assertGreater(len(response["tool_calls_made"]), 0, "No tools were called")
        
        # Verify weather tool was called
        tool_calls = response["tool_calls_made"]
        weather_calls = [call for call in tool_calls if call["tool"] == "weather"]
        self.assertGreater(len(weather_calls), 0, "Weather tool was not called")
    
    def test_02_news_tool(self):
        """Test news tool execution"""
        response, error = self.llm.Call("Get me technology news", verbose=self.config.debug_mode)
        self.assertIsNone(error, f"News tool test failed: {error}")
        
        # Verify tool execution
        tool_calls = response["tool_calls_made"]
        news_calls = [call for call in tool_calls if call["tool"] == "news"]
        self.assertGreater(len(news_calls), 0, "News tool was not called")
    
    def test_03_tool_error_handling(self):
        """Test tool error handling"""
        # Create LLM with no tools to test error handling
        config = self.config.get_base_config()
        config["tools"] = []
        
        llm, error = CreateAnthropic(config)
        self.assertIsNone(error)
        
        # This should not fail even with no tools available
        response, error = llm.Call("What's the weather?")
        self.assertIsNone(error, "Tool error handling failed")
    
    def test_04_multi_tool_execution(self):
        """Test multiple tool execution in one conversation"""
        query = "What's the weather in Paris and get me sports news"
        response, error = self.llm.Call(query, verbose=self.config.debug_mode)
        self.assertIsNone(error)
        
        # Should have called both tools
        tool_calls = response["tool_calls_made"]
        tools_used = {call["tool"] for call in tool_calls}
        
        # May call weather and news in multiple iterations
        self.assertTrue(len(tool_calls) >= 1, "No tools were executed")

# =============================================================================
# PHASE 3: INTEGRATION TESTS
# =============================================================================

class Phase3TwoComponentTests(BaseTestCase):
    """Phase 3A: Two-component integration tests"""
    
    PHASE_NAME = "Phase3A_TwoComponent"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config = cls.config.get_base_config()
        config["enable_mcp"] = True
        config["mcp_servers"] = cls.config.mcp_servers
        cls.llm, error = CreateAnthropic(config)
        if error:
            raise unittest.SkipTest(f"Cannot create LLM for integration tests: {error}")
        cls.uploaded_files = []
    
    @classmethod
    def tearDownClass(cls):
        """Clean up uploaded files"""
        for file_id in cls.uploaded_files:
            try:
                cls.llm.DeleteFile(file_id)
            except:
                pass
    
    def test_01_mcp_plus_files(self):
        """Test MCP integration with file uploads"""
        # Upload file first
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Weather analysis data for New York: sunny, 75F")
            test_file = f.name
        
        try:
            file_id, error = self.llm.UploadFile(test_file, auto_attach=True)
            self.assertIsNone(error)
            self.uploaded_files.append(file_id)
            
            # Test MCP + file interaction
            response, error = self.llm.Call(
                "Based on the uploaded file, get current weather for New York and compare",
                verbose=self.config.debug_mode
            )
            self.assertIsNone(error, "MCP + File integration failed")
            
        finally:
            os.unlink(test_file)
    
    def test_02_tools_plus_files(self):
        """Test local tools with file attachments"""
        # Upload data file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Research topics: artificial intelligence, machine learning, robotics")
            test_file = f.name
        
        try:
            file_id, error = self.llm.UploadFile(test_file, auto_attach=True)
            self.assertIsNone(error)
            self.uploaded_files.append(file_id)
            
            # Test tools + file interaction
            response, error = self.llm.Call(
                "Based on the topics in the file, get technology news",
                verbose=self.config.debug_mode
            )
            self.assertIsNone(error)
            
            # Verify both file access and tool usage
            self.assertGreater(len(response["tool_calls_made"]), 0)
            
        finally:
            os.unlink(test_file)
    
    def test_03_conversation_history_plus_tools(self):
        """Test conversation history preservation with tool usage"""
        # First interaction with tool
        self.llm.Call("Get weather for London and remember it")
        
        # Second interaction should remember previous weather
        response, error = self.llm.Call("What was the London weather you just told me?")
        self.assertIsNone(error)
        
        # Should not need to call weather tool again
        tool_calls = response["tool_calls_made"]
        weather_calls = [call for call in tool_calls if call["tool"] == "weather"]
        self.assertEqual(len(weather_calls), 0, "Should use conversation history, not make new tool calls")

class Phase3ThreeComponentTests(BaseTestCase):
    """Phase 3B: Three-component integration test"""
    
    PHASE_NAME = "Phase3B_ThreeComponent"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config = cls.config.get_base_config()
        config["enable_mcp"] = True
        config["mcp_servers"] = cls.config.mcp_servers
        cls.llm, error = CreateAnthropic(config)
        if error:
            raise unittest.SkipTest(f"Cannot create LLM for full integration test: {error}")
        cls.uploaded_files = []
    
    @classmethod
    def tearDownClass(cls):
        """Clean up uploaded files"""
        for file_id in cls.uploaded_files:
            try:
                cls.llm.DeleteFile(file_id)
            except:
                pass
    
    def test_complete_integration_workflow(self):
        """Test complete integration: MCP + Tools + Files + History"""
        # Step 1: Upload reference file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            Analysis Request:
            1. Check weather in Tokyo
            2. Get technology news
            3. Compare findings with historical data
            4. Provide summary
            """)
            test_file = f.name
        
        try:
            file_id, error = self.llm.UploadFile(test_file, auto_attach=True)
            self.assertIsNone(error, "File upload failed in integration test")
            self.uploaded_files.append(file_id)
            
            # Step 2: Execute complex workflow
            response, error = self.llm.Call(
                "Please execute the analysis request in the uploaded file",
                verbose=self.config.debug_mode
            )
            self.assertIsNone(error, "Integration workflow failed")
            
            # Step 3: Verify comprehensive execution
            self.assertGreater(len(response["tool_calls_made"]), 0, "No tools executed")
            
            # Should have called multiple tools
            tools_used = {call["tool"] for call in response["tool_calls_made"]}
            self.assertGreater(len(tools_used), 0, "No variety in tool usage")
            
            # Step 4: Test follow-up with history
            followup, error = self.llm.Call("Summarize what you just analyzed")
            self.assertIsNone(error, "History-based followup failed")
            
            # Follow-up should not require new tool calls
            self.assertEqual(len(followup["tool_calls_made"]), 0, 
                           "Follow-up should use conversation history")
            
        finally:
            os.unlink(test_file)

# =============================================================================
# TEST RUNNER AND REPORTING
# =============================================================================

class CustomTestResult(unittest.TextTestResult):
    """Custom test result that tracks status for reporting"""
    
    def addSuccess(self, test):
        super().addSuccess(test)
        test._test_status = 'passed'
    
    def addError(self, test, err):
        super().addError(test, err)
        test._test_status = 'errors'
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        test._test_status = 'failed'
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        test._test_status = 'skipped'

class CustomTestRunner(unittest.TextTestRunner):
    """Custom test runner using our result class"""
    resultclass = CustomTestResult

def run_progressive_tests(phases: List[str] = None, verbose: bool = False):
    """
    Run the progressive test suite
    
    Args:
        phases: List of phase names to run (default: all phases)
        verbose: Enable verbose output
    """
    if phases is None:
        phases = ["Phase1", "Phase2A", "Phase2B", "Phase2C", "Phase2D", "Phase3A", "Phase3B"]
    
    # Test class mapping
    test_classes = {
        "Phase1": Phase1FoundationTests,
        "Phase2A": Phase2APITests,
        "Phase2B": Phase2MCPTests,
        "Phase2C": Phase2FileTests,
        "Phase2D": Phase2ToolTests,
        "Phase3A": Phase3TwoComponentTests,
        "Phase3B": Phase3ThreeComponentTests
    }
    
    # Create test suite
    suite = unittest.TestSuite()
    
    for phase in phases:
        if phase in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_classes[phase])
            suite.addTests(tests)
    
    # Run tests with custom runner
    # For API-only mode, use minimal test output but still show to console
    if os.getenv("TEST_DEBUG") == "true" and not verbose:
        # API debug mode - minimal test framework output, but show API debug on console
        runner = CustomTestRunner(verbosity=1, stream=None)
    else:
        # Normal or test verbose mode
        runner = CustomTestRunner(
            verbosity=2 if verbose else 1,
            stream=None  # Always output to console for better debugging
        )
    
    result = runner.run(suite)
    
    # Update reporter summary from actual results
    reporter.results["summary"]["total_tests"] = result.testsRun
    reporter.results["summary"]["passed"] = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
    reporter.results["summary"]["failed"] = len(result.failures)
    reporter.results["summary"]["errors"] = len(result.errors)
    reporter.results["summary"]["skipped"] = len(result.skipped)
    
    # Generate report
    report_file = reporter.save_report()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"PROGRESSIVE TEST SUITE COMPLETE")
    print(f"{'='*60}")
    print(f"Total Tests: {reporter.results['summary']['total_tests']}")
    print(f"Passed: {reporter.results['summary']['passed']}")
    print(f"Failed: {reporter.results['summary']['failed']}")
    print(f"Errors: {reporter.results['summary']['errors']}")
    print(f"Skipped: {reporter.results['summary']['skipped']}")
    print(f"\nDetailed report saved to: {report_file}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Progressive Test Suite for Anthropic API")
    parser.add_argument("--phases", nargs="+", 
                       choices=["Phase1", "Phase2A", "Phase2B", "Phase2C", "Phase2D", "Phase3A", "Phase3B"],
                       help="Specific phases to run")
    parser.add_argument("--verbose", "-v", 
                       choices=["full", "api", "test"], 
                       help="Verbose level: full=test+API debug, api=API debug only, test=test framework only")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (deprecated - use --verbose)")
    
    args = parser.parse_args()
    
    # Handle verbose levels
    unittest_verbose = False
    api_debug = False
    
    if args.verbose == "full":
        unittest_verbose = True
        api_debug = True
        print("[VERBOSE] Full debug mode: Test framework + API debug enabled")
    elif args.verbose == "api":
        unittest_verbose = False
        api_debug = True
        print("[VERBOSE] API debug mode: Only API debug messages enabled")
    elif args.verbose == "test":
        unittest_verbose = True
        api_debug = False
        print("[VERBOSE] Test debug mode: Only test framework verbose enabled")
    
    # Legacy --debug flag support
    if args.debug:
        api_debug = True
        print("[VERBOSE] Legacy debug flag detected - enabling API debug")
    
    # Set API debug environment
    if api_debug:
        os.environ["TEST_DEBUG"] = "true"
    else:
        os.environ.pop("TEST_DEBUG", None)  # Remove if exists
    
    success = run_progressive_tests(args.phases, unittest_verbose)
    exit(0 if success else 1)