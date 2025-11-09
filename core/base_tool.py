from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import inspect
from core.logger import log_info, log_error
from core.exceptions import ToolError

class BaseTool(ABC):
    """
    Abstract base class for reusable tools within the MCP framework.
    Tools can represent local functions, API wrappers, or model utilities.
    """

    name: str = "BaseTool"
    description: str = "Generic tool interface"
    version: str = "1.0"
    async_supported: bool = False  # Indicates whether async calls are supported

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    # ---- core interface ----
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Synchronous tool execution logic (must be implemented)."""
        raise NotImplementedError

    async def aexecute(self, **kwargs) -> Any:
        """Asynchronous execution version (optional override)."""
        return self.execute(**kwargs)

    # ---- optional hooks ----
    def validate_input(self, **kwargs) -> bool:
        """Optional input validation before execution."""
        return True

    def post_process(self, result: Any) -> Any:
        """Optional post-processing hook for refining tool output."""
        return result

    def on_error(self, error: Exception, **kwargs) -> Dict[str, Any]:
        """Optional error handler for graceful fallback."""
        log_error(f"[{self.name}] tool execution error: {error}")
        return {"error": str(error), "tool": self.name}

    # ---- safe unified interface ----
    async def safe_execute(self, **kwargs) -> Union[Any, Dict[str, Any]]:
        """
        Unified safe entry point.
        Handles validation, logging, async/sync detection, and error management.
        """
        log_info(f"[{self.name}] tool started execution", kwargs=kwargs)

        try:
            # --- Input validation ---
            if not self.validate_input(**kwargs):
                raise ToolError(f"Invalid input for tool {self.name}", context=kwargs)

            # --- Determine execution mode ---
            if self.async_supported and inspect.iscoroutinefunction(self.aexecute):
                result = await self.aexecute(**kwargs)
            else:
                result = self.execute(**kwargs)

            # --- Post processing ---
            result = self.post_process(result)
            log_info(f"[{self.name}] tool completed successfully")
            return result

        except ToolError as e:
            log_error(f"[{self.name}] tool error: {e}")
            return self.on_error(e, **kwargs)

        except Exception as e:
            log_error(f"[{self.name}] unexpected exception: {e}")
            raise ToolError(str(e), context={"tool": self.name})

    # ---- callable alias (for syntactic sugar) ----
    async def __call__(self, **kwargs) -> Union[Any, Dict[str, Any]]:
        """Allow tools to be invoked like functions."""
        return await self.safe_execute(**kwargs)
