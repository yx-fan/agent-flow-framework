# core/exceptions.py
class MCPError(Exception):
    """Base exception for all MCP-related errors."""
    def __init__(self, message: str, *, context: dict | None = None):
        self.context = context or {}
        super().__init__(f"{self.__class__.__name__}: {message}")


class AgentError(MCPError):
    """Errors raised during agent execution."""


class ToolError(MCPError):
    """Errors raised during tool execution."""


class NodeError(MCPError):
    """Errors raised during node execution."""


class MemoryError(MCPError):
    """Errors raised when accessing or saving memory state."""


class ConfigError(MCPError):
    """Errors raised when configuration is missing or invalid."""


class RegistryError(MCPError):
    """Errors raised during registration or lookup of components."""


class MCPRuntimeError(MCPError):
    """Generic runtime error for orchestrator or system-level failures."""




# Example usage:
# raise AgentError("LLM API timeout", context={"agent": "QAAgent", "query": query})
