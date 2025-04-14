from typing import Dict, List, Any
import json

from agents.base_agent import BaseAgent
from models.model_implementations import GPT45Model, GPTO3MiniModel
from schemas.base import Message, ContentType


class GPT45Agent(BaseAgent):
    """An agent powered by the GPT-4.5 model."""
    
    def __init__(self, id: str = None, name: str = None):
        description = "An advanced reasoning agent powered by GPT-4.5"
        super().__init__(id, name or "GPT-4.5 Agent", description)
        self.model = GPT45Model()
        self.supported_functions = [
            "analyze_data",
            "complex_reasoning",
            "task_planning"
        ]
    
    def _process_message(self, message: Message) -> None:
        """Process an incoming message using the GPT-4.5 model."""
        print(f"GPT-4.5 Agent received: {message.id}")
        for content in message.content:
            if content.type == ContentType.TEXT:
                print(f"Content: {content.value[:100]}...")
    
    def generate_response(self, message: Message) -> Message:
        """Generate a response using the GPT-4.5 model."""
        prompt = self._format_prompt_from_message(message)
        
        # Convert conversation history to OpenAI format
        messages = [
            {"role": "system", "content": f"You are {self.name}, {self.description}. Follow the Agent-to-Agent protocol when communicating."}
        ]
        
        # Add relevant conversation history
        for msg in self.conversation_history[-5:]:  # Just use the last 5 messages for context
            if msg.sender_id == self.id:
                role = "assistant"
            else:
                role = "user"
                
            for content in msg.content:
                if content.type == ContentType.TEXT:
                    messages.append({"role": role, "content": content.value})
        
        # Generate the response
        response_text = self.model.generate_text(messages, temperature=0.7)
        
        # Create and return a new message
        return self.create_message(
            recipient_id=message.sender_id,
            content_value=response_text,
            content_type=ContentType.TEXT,
            in_reply_to=message.id
        )
    
    def _format_prompt_from_message(self, message: Message) -> str:
        """Format a prompt from a message for the GPT-4.5 model."""
        prompt_parts = []
        
        for content in message.content:
            if content.type == ContentType.TEXT:
                prompt_parts.append(content.value)
            elif content.type == ContentType.JSON:
                prompt_parts.append(f"JSON Data: {json.dumps(content.value, indent=2)}")
            else:
                prompt_parts.append(f"[Content of type {content.type} not directly processable as text]")
                
        return "\n".join(prompt_parts)


class GPTO3MiniAgent(BaseAgent):
    """An agent powered by the GPT-O3 Mini model."""
    
    def __init__(self, id: str = None, name: str = None):
        description = "An efficient assistant powered by GPT-O3 Mini"
        super().__init__(id, name or "GPT-O3 Mini Agent", description)
        self.model = GPTO3MiniModel()
        self.supported_functions = [
            "answer_questions",
            "summarize_text",
            "basic_reasoning"
        ]
    
    def _process_message(self, message: Message) -> None:
        """Process an incoming message using the GPT-O3 Mini model."""
        print(f"GPT-O3 Mini Agent received: {message.id}")
        for content in message.content:
            if content.type == ContentType.TEXT:
                print(f"Content: {content.value[:100]}...")
    
    def generate_response(self, message: Message) -> Message:
        """Generate a response using the GPT-O3 Mini model."""
        prompt = self._format_prompt_from_message(message)
        
        # Convert conversation history to OpenAI format
        messages = [
            {"role": "system", "content": f"You are {self.name}, {self.description}. Be concise and efficient in your responses."}
        ]
        
        # Add relevant conversation history (only a few for efficiency)
        for msg in self.conversation_history[-3:]:  # Just use the last 3 messages for context
            if msg.sender_id == self.id:
                role = "assistant"
            else:
                role = "user"
                
            for content in msg.content:
                if content.type == ContentType.TEXT:
                    messages.append({"role": role, "content": content.value})
        
        # Generate the response
        response_text = self.model.generate_text(messages, temperature=0.5, max_tokens=300)
        
        # Create and return a new message
        return self.create_message(
            recipient_id=message.sender_id,
            content_value=response_text,
            content_type=ContentType.TEXT,
            in_reply_to=message.id
        )
    
    def _format_prompt_from_message(self, message: Message) -> str:
        """Format a prompt from a message for the GPT-O3 Mini model."""
        # Similar to the GPT-4.5 agent but simpler for efficiency
        for content in message.content:
            if content.type == ContentType.TEXT:
                return content.value
        
        return "Please provide a text message."