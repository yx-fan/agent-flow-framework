# core/message_schema.py
from typing import Any, Dict, Optional, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator, ValidationError

class Message(BaseModel):
    """
    Standardized message schema for all Agent/Node/Tool communication.
    Compatible with LangGraph's 'messages' state.
    """

    role: Literal["human", "assistant", "tool", "system"]
    content: str = Field(..., description="The text or data of the message.")
    name: Optional[str] = Field(None, description="Name of the agent/tool emitting the message.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    # ---- lightweight validation ----
    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if not isinstance(v, str):
            raise ValueError("Message.content must be a string")
        if not v.strip():
            raise ValueError("Message.content cannot be empty")
        return v

    def to_langgraph(self) -> Dict[str, Any]:
        """Convert to LangGraph-compatible message dict."""
        return {
            "role": self.role,
            "content": self.content,
            "name": self.name,
            "metadata": self.metadata,
        }

    def short_repr(self) -> str:
        """Readable one-line summary."""
        return f"[{self.role.upper()}:{self.name}] {self.content[:80]}"

# ---- Utility constructors ----
def make_human_message(content: str, **kwargs) -> Message:
    return Message(role="human", content=content, **kwargs)

def make_ai_message(content: str, name: str = "assistant", **kwargs) -> Message:
    return Message(role="assistant", name=name, content=content, **kwargs)

def make_tool_message(content: str, name: str, **kwargs) -> Message:
    return Message(role="tool", name=name, content=content, **kwargs)
