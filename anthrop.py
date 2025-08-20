#!/usr/bin/env python3
# anthrop.py - Production-ready Anthropic API with MCP integration
import anthropic
import os
import json
import sys
from typing import List, Dict, Any, Optional, Tuple, Union


class AnthropicLLM:
    """
    LLM object that maintains conversational state and handles tool execution.
    """

    def __init__(self, client: anthropic.Anthropic, config: Dict[str, Any]):
        self.client = client
        self.model = config.get("model", "claude-sonnet-4-20250514")
        self.base_tools = config.get("tools", [])
        self.mcp_servers = config.get("mcp_servers", [])
        self.enable_mcp = config.get("enable_mcp", False)
        self.default_params = {
            "max_tokens": config.get("max_tokens", 40000),
            "temperature": config.get("temperature", 0.7),
            "thinking_budget_tokens": config.get("thinking_budget_tokens", 6000),
        }
        self.system_prompt = config.get("system_prompt", "")
        self.conversation_history = []
        self.debug_mode = config.get("debug", False)
        self.persistent_files = []
        self.debug_call_counter = 0

        # Enhanced debug configuration
        if isinstance(self.debug_mode, dict):
            self.debug_config = self.debug_mode
            self.debug_mode = self.debug_config.get("enabled", False)
        else:
            self.debug_config = {
                "enabled": self.debug_mode,
                "level": "full",
                "output": "console",
                "sections": {
                    "system_prompt": True,
                    "user_input": True,
                    "message_buffer": True,
                    "api_request": True,
                    "api_response": True,
                    "llm_response_content": True,
                    "timing": True,
                },
            }

    def Call(
        self,
        message: str,
        options: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Make a call to the LLM with optional parameter overrides.

        Args:
            message: User message to send
            options: Optional overrides for tools, temperature, etc.
                - additional_tools: List of tools to add to base tools
                - tools: List of tools to replace base tools entirely
                - temperature: Override temperature
                - max_tokens: Override max tokens
                - system_prompt: Override system prompt
            verbose: Enable debug output for this call (default: False)

        Returns:
            (response_dict, error_string)
        """
        if options is None:
            options = {}

        try:
            # Store options for debug output
            self._current_call_options = options if options else None

            # Resolve tools for this call
            tools_for_call = self._resolve_tools(options)

            # Resolve parameters for this call
            params = self._resolve_params(options)

            # Debug: Call start with user input
            self._print_comprehensive_debug(
                "call_start", message=message, system_prompt=self._get_system_prompt()
            )

            # Add user message to conversation history with file attachments
            if self.persistent_files:
                content_blocks = self._build_cached_content_blocks(
                    message, self.persistent_files
                )
                self.conversation_history.append(
                    {"role": "user", "content": content_blocks}
                )
            else:
                self.conversation_history.append({"role": "user", "content": message})

            if verbose:
                print(f"[DEBUG] User message added to history: {message}")

            # Execute the tool loop
            final_response, tool_calls_made = self._execute_tool_loop(
                tools_for_call, params, verbose
            )

            # Return clean response
            response = {
                "content": self._extract_text_content(final_response),
                "stop_reason": final_response.stop_reason,
                "tool_calls_made": tool_calls_made,
                "tokens_used": (
                    getattr(final_response.usage, "output_tokens", 0)
                    if hasattr(final_response, "usage")
                    else 0
                ),
            }

            return response, None

        except Exception as e:
            return None, f"Error in LLM call: {str(e)}"

    def _resolve_tools(self, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Resolve which tools to use for this call."""
        if "tools" in options:
            # Complete override
            return options["tools"]
        elif "additional_tools" in options:
            # Additive
            return self.base_tools + options["additional_tools"]
        else:
            # Default
            return self.base_tools

    def _resolve_params(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameters for this call."""
        params = self.default_params.copy()

        # Override with call-time options
        for key in ["max_tokens", "temperature", "thinking_budget_tokens"]:
            if key in options:
                params[key] = options[key]

        return params

    def _execute_tool_loop(
        self, tools: List[Dict[str, Any]], params: Dict[str, Any], verbose: bool = False
    ) -> Tuple[Any, List[Dict[str, Any]]]:
        """Execute the tool calling loop until completion."""
        all_tool_calls_made = []
        iteration = 0

        while True:
            iteration += 1
            if verbose:
                print(f"[DEBUG] Tool loop iteration {iteration}")

            # Determine system prompt for this call
            system_prompt = self._get_system_prompt()

            # Make LLM call
            call_params = {
                "model": self.model,
                "max_tokens": params["max_tokens"],
                "system": system_prompt,
                "messages": self.conversation_history,
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": params["thinking_budget_tokens"],
                },
                "stream": False,  # Explicitly disable streaming
            }

            # Only set temperature to 1 when thinking is enabled, otherwise omit it
            call_params["temperature"] = 1

            # Debug: API request details
            self._print_comprehensive_debug("api_request", call_params=call_params)

            # Add MCP servers and/or local tools
            if self.enable_mcp and self.mcp_servers:
                call_params["mcp_servers"] = self.mcp_servers
                call_params["betas"] = ["mcp-client-2025-04-04", "files-api-2025-04-14"]
                # Also include local tools alongside MCP servers  
                if tools:
                    call_params["tools"] = tools

                try:
                    # Use beta API for MCP support with hybrid tools
                    llm_response = self.client.beta.messages.create(
                        **call_params, timeout=600.0
                    )
                except Exception as e:
                    if verbose:
                        print(
                            f"[DEBUG] MCP beta API failed, falling back to local tools only: {e}"
                        )
                    # Fall back to local tools only
                    call_params.pop("mcp_servers", None)
                    if tools:
                        call_params["tools"] = tools
                    if self.persistent_files:
                        # Keep file API support even in fallback
                        call_params["betas"] = ["files-api-2025-04-14"]
                        llm_response = self.client.beta.messages.create(
                            **call_params, timeout=600.0
                        )
                    else:
                        call_params.pop("betas", None)
                        llm_response = self.client.messages.create(
                            **call_params, timeout=600.0
                        )
            else:
                # Use local tools only if no MCP servers configured
                if tools:
                    call_params["tools"] = tools
                if self.persistent_files:
                    # Use beta API for file support
                    call_params["betas"] = ["files-api-2025-04-14"]
                    llm_response = self.client.beta.messages.create(
                        **call_params, timeout=600.0
                    )
                else:
                    llm_response = self.client.messages.create(
                        **call_params, timeout=600.0
                    )

            # Debug: API response details
            self._print_comprehensive_debug("api_response", llm_response=llm_response)

            if verbose:
                self._print_debug_response(llm_response)

            # Add LLM response to conversation history
            self._add_assistant_response_to_history(llm_response)

            # Check if tools need to be executed
            if llm_response.stop_reason == "tool_use":
                tool_calls_this_iteration = self._execute_tools(llm_response, verbose)
                all_tool_calls_made.extend(tool_calls_this_iteration)

                if verbose:
                    print(
                        f"[DEBUG] Executed {len(tool_calls_this_iteration)} tools in iteration {iteration}"
                    )

                # Continue the loop
                continue
            else:
                # LLM finished - break the loop
                return llm_response, all_tool_calls_made

    def _get_system_prompt(self) -> str:
        """Get the system prompt to use."""
        return self.system_prompt

    def _execute_tools(
        self, llm_response, verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """Execute all tool calls in the LLM response."""
        tool_results_to_send_back = []
        tool_calls_made = []

        for block in llm_response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                tool_use_id = block.id

                if verbose:
                    print(
                        f"[DEBUG] Executing tool: {tool_name} with input {tool_input}"
                    )

                # Execute the tool (this is where you'd call your actual tool functions)
                try:
                    result = self._call_tool_function(tool_name, tool_input)

                    if verbose:
                        print(f"[DEBUG] Tool {tool_name} returned: {result}")

                    tool_calls_made.append(
                        {"tool": tool_name, "input": tool_input, "result": result}
                    )

                except Exception as e:
                    result = {"error": f"Tool execution failed: {str(e)}"}
                    if verbose:
                        print(f"[DEBUG] Tool {tool_name} failed: {result}")

                    tool_calls_made.append(
                        {"tool": tool_name, "input": tool_input, "result": result}
                    )

                # Prepare tool result for LLM
                tool_results_to_send_back.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(result),
                    }
                )

        # Add tool results to conversation history
        if tool_results_to_send_back:
            self.conversation_history.append(
                {"role": "user", "content": tool_results_to_send_back}
            )

        return tool_calls_made

    def _call_tool_function(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call the actual tool function. Override this method to integrate with your tools.
        This is a mock implementation based on your example.
        """
        if tool_name == "weather":
            return self._mock_weather(tool_input.get("location", ""))
        elif tool_name == "news":
            return self._mock_news(tool_input.get("topic", ""))
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _mock_weather(self, location: str) -> Dict[str, Any]:
        """Mock weather function from your example."""
        weather_data = {
            "New York": {"temperature": 72, "condition": "Sunny"},
            "London": {"temperature": 62, "condition": "Cloudy"},
            "Tokyo": {"temperature": 80, "condition": "Partly cloudy"},
            "Paris": {"temperature": 65, "condition": "Rainy"},
            "Sydney": {"temperature": 85, "condition": "Clear"},
            "Berlin": {"temperature": 60, "condition": "Foggy"},
        }
        return weather_data.get(
            location, {"error": f"No weather data available for {location}"}
        )

    def _mock_news(self, topic: str) -> Dict[str, Any]:
        """Mock news function from your example."""
        news_data = {
            "technology": [
                "New AI breakthrough announced by research lab",
                "Tech company releases latest smartphone model",
                "Quantum computing reaches milestone achievement",
            ],
            "sports": [
                "Local team wins championship game",
                "Star player signs record-breaking contract",
                "Olympic committee announces host city for 2036",
            ],
            "weather": [
                "Storm system developing in the Atlantic",
                "Record temperatures recorded across Europe",
                "Climate scientists release new research findings",
            ],
        }
        return {
            "headlines": news_data.get(
                topic.lower(), ["No news available for this topic"]
            )
        }

    def _add_assistant_response_to_history(self, llm_response):
        """Add LLM response to conversation history, preserving block objects."""
        assistant_response_content = []
        for block in llm_response.content:
            # Keep the original block objects - DO NOT convert to dictionaries
            assistant_response_content.append(block)

        self.conversation_history.append(
            {"role": "assistant", "content": assistant_response_content}
        )

    def _extract_text_content(self, llm_response) -> str:
        """Extract text content from LLM response."""
        text_parts = []
        for block in llm_response.content:
            if block.type == "text":
                text_parts.append(block.text)
        return "\n".join(text_parts)

    def _print_debug_response(self, response):
        """Debug printing based on your example."""
        print("\n==== LLM RESPONSE ====")
        for block in response.content:
            if block.type == "thinking":
                print("\n🧠 THINKING BLOCK:")
                print(block.thinking)
                if hasattr(block, "signature") and block.signature:
                    print(f"[Signature (first 50 chars): {block.signature[:50]}...]")
            elif block.type == "redacted_thinking":
                print("\n🔒 REDACTED THINKING BLOCK:")
                print(
                    f"[Data length: {len(block.data) if hasattr(block, 'data') else 'N/A'}]"
                )
            elif block.type == "text":
                print("\n✅ TEXT:")
                print(block.text)
            elif block.type == "tool_use":
                print("\n🛠️ TOOL USE REQUEST:")
                print(f"Tool: {block.name}")
                print(f"Input: {block.input}")
                print(f"Tool ID: {block.id}")
        print("==== END RESPONSE ====")

    def _print_comprehensive_debug(self, phase: str, **kwargs):
        """Print debug information showing raw API message structure"""
        if not self.debug_mode:
            return

        import json

        if phase == "call_start":
            self.debug_call_counter += 1
            user_request = kwargs.get("message", "")
            print(f"\n=== DEBUG Call #{self.debug_call_counter} ===")
            print(f"userrequest: {repr(user_request)}")

            # Show parameters if any options were provided
            if hasattr(self, "_current_call_options") and self._current_call_options:
                print(f"Parameters: {self._current_call_options}")

        elif phase == "api_request":
            call_params = kwargs.get("call_params", {})

            # Extract and show the message structure being sent to API
            messages = call_params.get("messages", [])
            system_prompt = call_params.get("system", "")

            print(f"system: {repr(system_prompt)}")

            # Show each message in the conversation
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")

                if isinstance(content, list):
                    # Handle complex content blocks
                    content_summary = []
                    for block in content:
                        if hasattr(block, "type"):
                            if block.type == "text":
                                content_summary.append(getattr(block, "text", ""))
                            elif block.type == "document":
                                content_summary.append("[DOCUMENT]")
                            elif block.type == "tool_use":
                                content_summary.append(
                                    f"[TOOL: {getattr(block, 'name', 'unknown')}]"
                                )
                            elif block.type == "tool_result":
                                content_summary.append("[TOOL_RESULT]")
                            else:
                                content_summary.append(f"[{block.type}]")
                        elif isinstance(block, dict):
                            if block.get("type") == "text":
                                content_summary.append(block.get("text", ""))
                            elif block.get("type") == "document":
                                content_summary.append("[DOCUMENT]")
                            elif block.get("type") == "tool_result":
                                content_summary.append("[TOOL_RESULT]")
                            else:
                                content_summary.append(str(block))
                    content_str = " ".join(content_summary)
                else:
                    content_str = str(content)

                print(f"{role}: {repr(content_str)}")

        elif phase == "api_response":
            llm_response = kwargs.get("llm_response")
            if llm_response and hasattr(llm_response, "content"):
                response_parts = []

                for block in llm_response.content:
                    if hasattr(block, "type"):
                        if block.type == "text":
                            response_parts.append(getattr(block, "text", ""))
                        elif block.type == "thinking":
                            thinking_content = getattr(block, "thinking", "")
                            response_parts.append(
                                f"[THINKING: {thinking_content[:100]}...]"
                            )
                        elif block.type == "tool_use":
                            tool_name = getattr(block, "name", "unknown")
                            tool_input = getattr(block, "input", {})
                            response_parts.append(
                                f"[TOOL_USE: {tool_name} - {tool_input}]"
                            )
                        else:
                            response_parts.append(f"[{block.type}]")

                response_str = " ".join(response_parts)
                print(f"response: {repr(response_str)}")

                # Show stop reason and token usage
                stop_reason = getattr(llm_response, "stop_reason", "unknown")
                tokens_used = (
                    getattr(llm_response.usage, "output_tokens", 0)
                    if hasattr(llm_response, "usage")
                    else 0
                )
                print(f"stop_reason: {stop_reason}, tokens: {tokens_used}")

            print("=== END DEBUG ===\n")

    # State management methods
    def Reset(self):
        """Clear conversation history."""
        self.conversation_history = []
        if self.debug_mode:
            print("[DEBUG] Conversation history reset")

    def GetHistory(self) -> List[Dict[str, Any]]:
        """Get current conversation history."""
        return self.conversation_history.copy()

    def LoadHistory(self, messages: List[Dict[str, Any]]):
        """Load conversation history."""
        self.conversation_history = messages.copy()
        if self.debug_mode:
            print(f"[DEBUG] Loaded conversation history with {len(messages)} messages")

    def SetSystemPrompt(self, prompt: str):
        """Update system prompt."""
        self.system_prompt = prompt
        if self.debug_mode:
            print(f"[DEBUG] System prompt updated")

    def UploadFile(
        self, file_path: str, auto_attach: bool = True
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Upload a file to Anthropic and optionally auto-attach to all future messages.

        Args:
            file_path: Path to the file to upload
            auto_attach: If True, attach this file to all future conversations

        Returns:
            (file_id, error_string)
        """
        import tempfile
        import shutil

        try:
            if not os.path.exists(file_path):
                return None, f"File not found: {file_path}"

            # Check if file is text-based but has unsupported MIME type
            text_extensions = {
                ".md",
                ".py",
                ".js",
                ".html",
                ".css",
                ".json",
                ".xml",
                ".yaml",
                ".yml",
                ".sh",
                ".bat",
                ".sql",
                ".csv",
            }
            file_ext = os.path.splitext(file_path)[1].lower()

            temp_file = None
            upload_path = file_path

            if file_ext in text_extensions:
                # Create temporary .txt copy to force plain text MIME type
                temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
                shutil.copy2(file_path, temp_file.name)
                upload_path = temp_file.name
                temp_file.close()

                if self.debug_mode:
                    print(
                        f"[DEBUG] Created .txt copy for text file: {file_path} -> {upload_path}"
                    )

            try:
                with open(upload_path, "rb") as f:
                    file_response = self.client.beta.files.upload(
                        file=f, betas=["files-api-2025-04-14"]
                    )
            finally:
                # Clean up temporary file
                if temp_file and os.path.exists(upload_path):
                    os.unlink(upload_path)

            file_id = file_response.id

            if auto_attach and file_id not in self.persistent_files:
                self.persistent_files.append(file_id)

            if self.debug_mode:
                print(f"[DEBUG] File uploaded: {file_path} -> {file_id}")
                if auto_attach:
                    print(f"[DEBUG] File added to persistent files list")

            return file_id, None

        except Exception as e:
            return None, f"Error uploading file: {str(e)}"

    def DeleteFile(self, file_id: str) -> bool:
        """
        Delete a file from Anthropic and remove from persistent files.

        Args:
            file_id: File ID to delete

        Returns:
            True if successful, False if error
        """
        try:
            self.client.beta.files.delete(file_id, betas=["files-api-2025-04-14"])

            if file_id in self.persistent_files:
                self.persistent_files.remove(file_id)

            if self.debug_mode:
                print(f"[DEBUG] File deleted: {file_id}")

            return True

        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error deleting file {file_id}: {str(e)}")
            return False

    def ListFiles(self) -> List[Dict[str, Any]]:
        """
        List all files uploaded to Anthropic.

        Returns:
            List of file metadata dictionaries
        """
        try:
            files_response = self.client.beta.files.list(betas=["files-api-2025-04-14"])
            files_list = []

            for file_obj in files_response.data:
                files_list.append(
                    {
                        "id": file_obj.id,
                        "name": getattr(file_obj, "filename", "unknown"),
                        "size": getattr(file_obj, "size_bytes", 0),
                        "type": getattr(file_obj, "mime_type", "unknown"),
                        "created_at": getattr(file_obj, "created_at", None),
                        "is_persistent": file_obj.id in self.persistent_files,
                    }
                )

            if self.debug_mode:
                print(f"[DEBUG] Listed {len(files_list)} files")

            return files_list

        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error listing files: {str(e)}")
            return []

    def _build_cached_content_blocks(
        self, message: str, files: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Build content blocks with file attachments and caching optimization.

        Args:
            message: User message text
            files: List of file IDs to attach

        Returns:
            List of content blocks with cache control
        """
        content_blocks = []

        for file_id in files:
            content_blocks.append(
                {
                    "type": "document",
                    "source": {"type": "file", "file_id": file_id},
                    "cache_control": {"type": "ephemeral"},
                }
            )

        content_blocks.append({"type": "text", "text": message})

        return content_blocks


def CreateAnthropic(
    config: Dict[str, Any],
) -> Tuple[Optional[AnthropicLLM], Optional[str]]:
    """
    Factory function to create an Anthropic LLM object.

    Args:
        config: Configuration dictionary with keys:
            - model: Model name (default: claude-3-sonnet-20241022)
            - api_key: API key (optional if ANTHROPIC_API_KEY env var set)
            - tools: List of tool definitions
            - temperature: Default temperature (default: 0.7)
            - max_tokens: Default max tokens (default: 4000)
            - thinking_budget_tokens: Thinking tokens budget (default: 2000)
            - system_prompt: System prompt (optional)
            - debug: Enable debug mode (default: False)

    Returns:
        (llm_object, error_string)
    """
    try:
        # Set up API key
        api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return (
                None,
                "ERROR: Please provide api_key in config or set ANTHROPIC_API_KEY environment variable",
            )

        # Create client
        client = anthropic.Anthropic(api_key=api_key)

        # Create and return LLM object
        llm = AnthropicLLM(client, config)
        return llm, None

    except Exception as e:
        return None, f"Error creating Anthropic client: {str(e)}"


# Example usage and tools from your original code
def create_example_tools():
    """Create example tools based on your original code."""
    return [
        {
            "name": "weather",
            "description": "Get current weather information for a location.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get weather for.",
                    }
                },
                "required": ["location"],
            },
        },
        {
            "name": "news",
            "description": "Get latest news headlines for a topic.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to get news about.",
                    }
                },
                "required": ["topic"],
            },
        },
    ]
