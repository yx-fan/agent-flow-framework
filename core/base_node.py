# core/base_node.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from core.logger import log_info, log_error
from core.exceptions import NodeError, AgentError

class BaseNode(ABC):
    """
    Abstract base node for LangGraph-compatible workflow nodes.
    Nodes can represent Agents, Tools, or control logic (reflection, loop, etc).
    """

    name: str = "BaseNode"
    description: str = "Generic workflow node"
    node_type: str = "generic"  # e.g., "agent", "tool", "reflection", "control"

    def __init__(self, agent=None, tools: Optional[list] = None):
        self.agent = agent              # Optional: Agent instance
        self.tools = tools or []        # Optional: Tool injection

    # ---- main execution interface ----
    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute node logic asynchronously and return updated state."""
        pass

    # ---- optional lifecycle hooks ----
    async def pre_execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-execution hook for setup or validation."""
        return state

    async def post_execute(self, state: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-execution hook for result processing or state updates."""
        return result

    async def on_error(self, error: Exception, state: Dict[str, Any]) -> Dict[str, Any]:
        """Error handler to allow graceful fallback or logging."""
        log_error(f"[{self.name}] execution failed: {error}")
        return {"error": str(error), "node": self.name}

    # ---- safe wrapper ----
    async def safe_execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unified execution wrapper.
        Handles pre/post hooks, logging, and error capture.
        """
        log_info(f"[{self.name}] node started execution", state_keys=list(state.keys()))

        try:
            # --- pre hook ---
            state = await self.pre_execute(state)

            # --- main logic ---
            result = await self.execute(state)

            # --- post hook ---
            result = await self.post_execute(state, result)

            log_info(f"[{self.name}] node completed successfully")
            return result

        except AgentError as e:
            log_error(f"[{self.name}] agent failed: {e}")
            return await self.on_error(e, state)

        except Exception as e:
            log_error(f"[{self.name}] unexpected error: {e}")
            raise NodeError(str(e), context={"node": self.name})

    # ---- helper methods ----
    def get_agent_name(self) -> Optional[str]:
        return getattr(self.agent, "name", None)

    def get_description(self) -> str:
        return getattr(self.agent, "description", self.description)
