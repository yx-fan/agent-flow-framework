# core/memory_interface.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import datetime

class MemoryInterface(ABC):
    """
    Abstract interface for both short-term (session) and long-term (vector) memory.
    Compatible with LangGraph's state system and LangChain memory concepts.
    """

    # ---- Core methods ----
    @abstractmethod
    async def load_state(self, session_id: str) -> Dict[str, Any]:
        """Load the full memory state for a given session/user."""
        pass

    @abstractmethod
    async def save_state(self, session_id: str, state: Dict[str, Any]):
        """Persist the memory or state for a given session/user."""
        pass

    @abstractmethod
    async def clear_state(self, session_id: str):
        """Clear all stored memory for a given session (reset or timeout)."""
        pass

    # ---- Message-level operations ----
    @abstractmethod
    async def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Append a single message to memory (short-term conversation)."""
        pass

    @abstractmethod
    async def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = 10,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent conversation messages."""
        pass

    # ---- Long-term memory operations (vector memory / recall) ----
    async def store_vector(
        self,
        session_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Optional: Store an embedding into long-term memory."""
        pass

    async def search_vector(
        self,
        session_id: str,
        query_vector: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Optional: Retrieve similar past memories by embedding similarity."""
        return []

    # ---- Utility ----
    async def summarize_session(self, session_id: str) -> str:
        """Optional: Return a concise summary of current session memory."""
        messages = await self.get_messages(session_id)
        if not messages:
            return ""
        joined = " ".join([m["content"] for m in messages[-10:]])
        return f"Session summary: {joined[:300]}..."

    async def metadata(self, session_id: str) -> Dict[str, Any]:
        """Optional: return memory statistics or metadata (size, last update)."""
        return {"session_id": session_id, "timestamp": datetime.datetime.utcnow().isoformat()}
