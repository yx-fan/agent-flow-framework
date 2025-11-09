# core/base_agent.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from core.memory_interface import MemoryInterface
from core.base_tool import BaseTool
from core.logger import log_info, log_error
from core.exceptions import AgentError, ToolError, MemoryError

class BaseAgent(ABC):
    """
    Base class for all AI Agents in the MCP framework.
    Each Agent handles one specialized capability (e.g., QA, Service, VIN).
    """

    name: str = "BaseAgent"
    description: str = "Generic agent interface"

    def __init__(
        self,
        memory: Optional[MemoryInterface] = None,
        tools: Optional[List[BaseTool]] = None,
    ):
        self.memory = memory
        self.tools = tools or []

    # ---- core interface ----
    @abstractmethod
    def run(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with the given query and context state.
        Returns a dictionary containing structured output and metadata.
        """
        pass

    # ---- optional hooks ----
    def pre_process(self, query: str, state: Dict[str, Any]) -> str:
        """Optional hook: normalize or enrich query before main execution."""
        return query

    def post_process(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Optional hook: refine or structure the agent's output."""
        return output

    # ---- utility methods ----
    def recall(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Fetch context or conversation memory (short/long-term)."""
        if not self.memory:
            return None
        try:
            log_info(f"[{self.name}] recalling memory", context_id=context_id)
            return self.memory.read(context_id)
        except Exception as e:
            log_error(f"[{self.name}] memory recall failed: {e}")
            raise MemoryError(str(e), context={"agent": self.name, "context_id": context_id})

    def remember(self, context_id: str, content: Dict[str, Any]) -> None:
        """Persist state or conversation to memory."""
        if not self.memory:
            return
        try:
            log_info(f"[{self.name}] saving memory", context_id=context_id)
            self.memory.write(context_id, content)
        except Exception as e:
            log_error(f"[{self.name}] memory write failed: {e}")
            raise MemoryError(str(e), context={"agent": self.name, "context_id": context_id})

    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Find and execute a registered tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    log_info(f"[{self.name}] using tool {tool_name}", params=kwargs)
                    result = tool.safe_execute(**kwargs) if hasattr(tool, "safe_execute") else tool.execute(**kwargs)
                    log_info(f"[{self.name}] tool {tool_name} completed successfully")
                    return result
                except Exception as e:
                    log_error(f"[{self.name}] tool {tool_name} failed: {e}")
                    raise ToolError(str(e), context={"agent": self.name, "tool": tool_name, "params": kwargs})
        raise ToolError(f"Tool '{tool_name}' not found", context={"agent": self.name})

    # ---- advanced hooks ----
    def reflect(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Optional: evaluate output quality and propose self-correction."""
        return output

    def clarify(self, query: str) -> Optional[str]:
        """Optional: ask clarifying question if input is ambiguous."""
        return None

    # ---- safe wrapper for consistent logging & errors ----
    def safe_run(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wrapper around `run()` that adds logging, hooks, and unified error handling.
        """
        log_info(f"Agent {self.name} started execution", query=query)
        try:
            processed_query = self.pre_process(query, state)
            result = self.run(processed_query, state)
            result = self.post_process(result)
            log_info(f"Agent {self.name} completed successfully")
            return result
        except Exception as e:
            log_error(f"Agent {self.name} failed: {e}")
            raise AgentError(str(e), context={"agent": self.name, "query": query})
