import os
import json
import random
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv

# Keep the mock classes for fallback/testing purposes
class MockCompletionResponse:
    """Mock response for development purposes to avoid API calls"""
    def __init__(self, content):
        self.content = content
        self.function_call = None
        self.tool_calls = []


class MockCompletionChoice:
    """Mock choice object for development"""
    def __init__(self, content):
        self.message = MockCompletionResponse(content)


class MockCompletionResult:
    """Mock completion result for development"""
    def __init__(self, content):
        self.choices = [MockCompletionChoice(content)]


class MockChatCompletions:
    """Mock chat completions class"""
    def create(self, model=None, messages=None, temperature=0.7, max_tokens=500, **kwargs):
        """Mock create method that returns predefined responses based on the input"""
        # Extract the last message content if available
        last_message = None
        for m in reversed(messages):
            if m.get("content"):
                last_message = m.get("content")
                break
        
        # Generate predefined responses based on content keywords
        if last_message and ("Agent-to-Agent Protocol" in last_message or "A2A" in last_message):
            response = """
The Agent-to-Agent (A2A) Protocol is a standardized communication framework enabling AI agents to interact effectively. 

Key components include:
1. Message structure with sender/recipient information
2. Content types (text, JSON, binary, etc.)
3. Function calling mechanisms for agent capabilities
4. Conversation session management

The protocol facilitates seamless collaboration between different agent systems.
"""
        elif last_message and "how message exchange works" in last_message.lower():
            response = """
Message exchange in the A2A protocol works through standardized formats:

1. Each message has a unique identifier, sender ID, recipient ID, and timestamp
2. Messages can contain multiple content items of different types
3. Messages can reference previous messages through the in_reply_to field
4. Agents acknowledge receipt and process messages according to their capabilities

This standardization ensures reliable communication between diverse agent systems.
"""
        elif last_message and "key components" in last_message.lower():
            response = """
Thank you for your question about the A2A protocol. Based on your research needs, here are the key points:

1. Core A2A Principles: Standardization, interoperability, security, and extensibility

2. Message Exchange: Uses structured JSON messages with required fields (IDs, content) and optional metadata. Messages flow through secure channels with delivery confirmation.

3. Standardized Schemas: Essential for cross-agent compatibility, enabling agents from different developers to communicate without custom integration work.

Would you like me to elaborate on any specific aspect?
"""
        elif last_message:
            response = f"This is a mock response for demonstration purposes. I received: {last_message[:100]}..."
        else:
            response = "This is a default mock response for demonstration purposes."
            
        return MockCompletionResult(response.strip())


class MockAzureOpenAI:
    """Mock Azure OpenAI client for development purposes"""
    def __init__(self, **kwargs):
        """Initialize with mock chat completions"""
        self.chat = type('obj', (object,), {
            'completions': MockChatCompletions()
        })


class OpenAIModel:
    """Base class for OpenAI model wrappers"""
    
    def __init__(self, model_name: str, config_prefix: str = None):
        """
        Initialize the model with specific configurations.
        
        Args:
            model_name: The name of the model to use
            config_prefix: The prefix for environment variables (e.g., "GPT45" or "O3_MINI")
        """
        load_dotenv()
        
        if config_prefix:
            self.endpoint = os.getenv(f"AZURE_OPENAI_ENDPOINT_{config_prefix}")
            self.api_key = os.getenv(f"AZURE_OPENAI_KEY_{config_prefix}")
            self.deployment = os.getenv(f"AZURE_OPENAI_DEPLOYMENT_{config_prefix}")
        else:
            self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            self.api_key = os.getenv("AZURE_OPENAI_KEY") 
            self.deployment = model_name
            
        self.model_name = model_name
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
        
        try:
            # Import the OpenAI library which supports both OpenAI and Azure OpenAI
            from openai import AzureOpenAI
            
            # Initialize client with Azure OpenAI settings
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            print(f"Initialized Azure OpenAI client for {model_name} using deployment {self.deployment}")
        except (ImportError, Exception) as e:
            # Fall back to mock client if there's an error
            print(f"Warning: Failed to initialize Azure OpenAI client: {str(e)}")
            print(f"Using mock OpenAI client for {model_name} instead")
            self.client = MockAzureOpenAI()
    
    def generate_text(self, messages: List[Dict[str, str]], max_tokens: int = 500) -> str:
        """
        Generate text using the OpenAI model.
        
        Args:
            messages: List of message dictionaries with "role" and "content" keys
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated text response
        """
        try:
            # Only pass parameters that are supported by the API
            response = self.client.chat.completions.create(
                model=self.deployment,  # Use deployment name for Azure OpenAI
                messages=messages,
                max_completion_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating text: {e}")
            return f"Error: {str(e)}"
    
    def generate_with_function_calling(
        self, 
        messages: List[Dict[str, str]], 
        functions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate text with function calling capability.
        
        Args:
            messages: List of message dictionaries
            functions: List of function definitions
            
        Returns:
            Dict containing the response or function call
        """
        try:
            # Convert functions to tools format for newer API
            tools = [{"type": "function", "function": func} for func in functions]
            
            # Only pass parameters that are supported by the API
            response = self.client.chat.completions.create(
                model=self.deployment,  # Use deployment name for Azure OpenAI
                messages=messages,
                tools=tools
            )
            
            message = response.choices[0].message
            
            # Check if there's a tool call
            if message.tool_calls and len(message.tool_calls) > 0:
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                return {
                    "type": "function_call",
                    "function_name": function_name,
                    "arguments": arguments
                }
            else:
                return {
                    "type": "message",
                    "content": message.content
                }
                
        except Exception as e:
            print(f"Error with function calling: {e}")
            return {"type": "error", "content": str(e)}