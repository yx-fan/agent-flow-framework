from typing import Any, Dict, List, Optional
from core.message_schema import Message
from core.logger import get_logger, log_debug, log_error, log_warning
from core.exceptions import MemoryError
from core.registry import MemoryRegistry
from core.config import CurrentConfig

logger = get_logger("StateManager")


class StateManager:
    """
    Centralized session state and memory handler.
    Acts as the bridge between orchestrator and memory backend.
    """

    def __init__(self):
        self.memory = MemoryRegistry.get_active_memory()
        logger.info(f"StateManager initialized with backend = {CurrentConfig.MEMORY_TYPE}")

    # ---- Core state operations ----
    async def load_state(self, session_id: str) -> Dict[str, Any]:
        try:
            state = await self.memory.load_state(session_id)
            log_debug("Loaded session state.", session_id=session_id, keys=list(state.keys()) if state else [])
            return state or {}
        except Exception as e:
            log_error("Failed to load state.", session_id=session_id, error=str(e))
            raise MemoryError("Failed to load state.", context={"session_id": session_id}) from e

    async def save_state(self, session_id: str, state: Dict[str, Any]):
        try:
            await self.memory.save_state(session_id, state)
            log_debug("State saved successfully.", session_id=session_id, state_size=len(state))
        except Exception as e:
            log_error("Failed to save state.", session_id=session_id, error=str(e))
            raise MemoryError("Failed to save state.", context={"session_id": session_id}) from e

    # ---- Message-level memory ----
    async def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        try:
            message = Message(role=role, content=content, metadata=metadata or {})
            await self.memory.append_message(session_id, role=message.role, content=message.content, metadata=message.metadata)
            log_debug("Message appended to session memory.", session_id=session_id, role=role)
        except Exception as e:
            log_error("Failed to append message.", session_id=session_id, role=role, error=str(e))
            raise MemoryError("Failed to append message.", context={"session_id": session_id}) from e

    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            msgs = await self.memory.get_messages(session_id, limit=limit)
            log_debug("Retrieved recent messages.", session_id=session_id, count=len(msgs))
            return msgs
        except Exception as e:
            log_warning("Failed to get messages.", session_id=session_id, error=str(e))
            return []

    # ---- Memory-level operations ----
    async def update_memory(self, session_id: str, result: Dict[str, Any]):
        try:
            content = result.get("content") or str(result)
            await self.memory.store_vector(session_id, embedding=[], metadata={"content": content})
            log_debug("Semantic memory updated.", session_id=session_id)
        except Exception as e:
            log_warning("Skipped memory update due to error.", session_id=session_id, error=str(e))

    # ---- Utility ----
    async def summarize_session(self, session_id: str) -> str:
        msgs = await self.get_recent_messages(session_id)
        if not msgs:
            return "No history available."
        joined = " ".join([m["content"] for m in msgs[-5:]])
        summary = f"Recent summary: {joined[:200]}"
        log_debug("Session summary generated.", session_id=session_id, length=len(summary))
        return summary
