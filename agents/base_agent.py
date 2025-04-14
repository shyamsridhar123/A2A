import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from schemas.base import AgentSpec, Message, Content, ContentType


class BaseAgent(ABC):
    """Base class for all agents in the A2A protocol."""
    
    def __init__(self, id: str = None, name: str = None, description: str = None, version: str = "1.0"):
        """Initialize the base agent with its identity information."""
        self.id = id or str(uuid.uuid4())
        self.name = name or self.__class__.__name__
        self.description = description or "A2A Protocol Compatible Agent"
        self.version = version
        self.supported_protocols = ["a2a-2023"]
        self.supported_functions = []
        self.conversation_history: List[Message] = []
        
    def get_spec(self) -> AgentSpec:
        """Get the agent's specification."""
        return AgentSpec(
            id=self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            supported_protocols=self.supported_protocols,
            supported_functions=self.supported_functions
        )
    
    def create_message(
        self, 
        recipient_id: str, 
        content_value: Any, 
        content_type: ContentType = ContentType.TEXT,
        in_reply_to: Optional[str] = None
    ) -> Message:
        """Create a message to be sent to another agent."""
        message = Message(
            id=str(uuid.uuid4()),
            sender_id=self.id,
            recipient_id=recipient_id,
            content=[
                Content(type=content_type, value=content_value)
            ],
            timestamp=datetime.utcnow(),
            metadata={},
            in_reply_to=in_reply_to,
            sequence_num=len(self.conversation_history) + 1
        )
        
        self.conversation_history.append(message)
        return message
    
    def receive_message(self, message: Message) -> None:
        """
        Process an incoming message from another agent.
        
        Args:
            message: The message to process
        """
        # Validate that this agent is the intended recipient
        if message.recipient_id != self.id:
            print(f"Warning: Message {message.id} not intended for this agent")
            return
            
        # Add to conversation history
        self.conversation_history.append(message)
        
        # Process the message
        self._process_message(message)
    
    @abstractmethod
    def _process_message(self, message: Message) -> None:
        """
        Process an incoming message. This method should be implemented by subclasses.
        
        Args:
            message: The message to process
        """
        pass
    
    @abstractmethod
    def generate_response(self, message: Message) -> Message:
        """
        Generate a response to a message. This method should be implemented by subclasses.
        
        Args:
            message: The message to respond to
            
        Returns:
            The response message
        """
        pass