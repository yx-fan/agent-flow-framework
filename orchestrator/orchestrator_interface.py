# orchestrator/orchestrator_interface.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class OrchestratorInterface(ABC):
    """
    Abstract interface for the MCP orchestrator.
    Defines the unified lifecycle for handling user queries and managing multi-agent workflows.
    """

    # ---- Core entrypoints ----
    @abstractmethod
    async def handle_user_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """
        Main entrypoint for handling a user query.
        Responsible for intent detection, routing, and invoking the correct workflow.
        """
        pass

    @abstractmethod
    async def run_graph(self, intent: str, query: str, session_id: str) -> Dict[str, Any]:
        """
        Execute the corresponding LangGraph workflow for a specific intent.
        Should return structured results including messages, outputs, and metadata.
        """
        pass

    # ---- Lifecycle hooks ----
    async def pre_process(self, query: str, session_id: str) -> str:
        """Optional: Clean or enrich query before intent detection."""
        return query

    async def post_process(self, result: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Optional: Refine final result before returning to API layer."""
        return result

    # ---- Memory / State integration ----
    async def load_session_state(self, session_id: str) -> Dict[str, Any]:
        """Optional: Retrieve persisted session state before execution."""
        return {}

    async def save_session_state(self, session_id: str, state: Dict[str, Any]):
        """Optional: Persist updated state after execution."""
        pass

    # ---- Error handling ----
    async def on_error(self, error: Exception, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Unified error handler for all orchestrator operations."""
        return {"error": str(error), "session_id": session_id}
