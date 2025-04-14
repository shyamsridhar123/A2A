from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    TEXT = "text"
    JSON = "json"
    BINARY = "binary"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"


class Content(BaseModel):
    type: ContentType = Field(..., description="The type of content")
    value: Any = Field(..., description="The content value")


class Message(BaseModel):
    id: str = Field(..., description="Unique message identifier")
    sender_id: str = Field(..., description="ID of the sending agent")
    recipient_id: str = Field(..., description="ID of the receiving agent")
    content: List[Content] = Field(..., description="List of content items")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the message was created")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")
    in_reply_to: Optional[str] = Field(None, description="ID of the message this is a reply to")
    sequence_num: Optional[int] = Field(None, description="Position of this message in a sequence")


class FunctionCall(BaseModel):
    function_name: str = Field(..., description="Name of the function to call")
    arguments: Dict[str, Any] = Field(..., description="Arguments for the function")


class FunctionResult(BaseModel):
    function_name: str = Field(..., description="Name of the function that was called")
    result: Any = Field(..., description="Result of the function call")
    error: Optional[str] = Field(None, description="Error message if the function call failed")


class AgentSpec(BaseModel):
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Human-readable name of the agent")
    description: str = Field(..., description="Description of the agent's capabilities")
    version: str = Field(..., description="Agent version")
    supported_protocols: List[str] = Field(default_factory=list, description="Protocols supported by the agent")
    supported_functions: List[str] = Field(default_factory=list, description="Functions supported by the agent")


class ConversationSession(BaseModel):
    id: str = Field(..., description="Unique conversation identifier")
    participants: List[str] = Field(..., description="List of agent IDs participating in the conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Message] = Field(default_factory=list)