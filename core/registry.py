from typing import Type, Dict, Any, Optional, Union
from core.logger import log_info, log_error
from core.exceptions import RegistryError, ConfigError
from core.base_agent import BaseAgent
from core.base_tool import BaseTool
from core.base_node import BaseNode
from core.memory_interface import MemoryInterface
from core.config import CurrentConfig


class BaseRegistry:
    """Generic registry base class for all MCP components."""

    _registry: Dict[str, Any] = {}
    component_type: str = "component"

    @classmethod
    def register(cls, name: str, component: Union[Type, Any], override: bool = False):
        if name in cls._registry and not override:
            raise RegistryError(
                f"[{cls.component_type}] '{name}' already registered.",
                context={"name": name, "type": cls.component_type},
            )
        cls._registry[name] = component
        log_info(f"[{cls.component_type}] registered", name=name)

    @classmethod
    def get(cls, name: str) -> Optional[Any]:
        return cls._registry.get(name)

    @classmethod
    def list(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def create_instance(cls, name: str, **kwargs) -> Any:
        try:
            component = cls.get(name)
            if component is None:
                raise RegistryError(
                    f"[{cls.component_type}] '{name}' not found.",
                    context={"name": name, "type": cls.component_type},
                )

            if isinstance(component, type):
                instance = component(**kwargs)
                log_info(f"[{cls.component_type}] instance created", name=name)
                return instance

            log_info(f"[{cls.component_type}] existing instance returned", name=name)
            return component

        except Exception as e:
            log_error(f"[{cls.component_type}] create_instance failed: {e}")
            raise RegistryError(str(e), context={"name": name, "type": cls.component_type})

    @classmethod
    def clear(cls):
        cls._registry.clear()
        log_info(f"[{cls.component_type}] registry cleared")


# ---- Specialized registries ----

class AgentRegistry(BaseRegistry):
    component_type = "agent"
    _registry: Dict[str, Type[BaseAgent]] = {}


class ToolRegistry(BaseRegistry):
    component_type = "tool"
    _registry: Dict[str, Type[BaseTool]] = {}


class NodeRegistry(BaseRegistry):
    component_type = "node"
    _registry: Dict[str, Type[BaseNode]] = {}


class MemoryRegistry(BaseRegistry):
    component_type = "memory"
    _registry: Dict[str, Type[MemoryInterface]] = {}

    @classmethod
    def autoload(cls):
        """Auto-register available memory backends based on config."""
        try:
            from memory.redis_memory import RedisMemory
            from memory.vector_memory import VectorMemory

            cls.register("redis", RedisMemory, override=True)
            cls.register("vector", VectorMemory, override=True)
            log_info("[memory] default backends registered")
        except Exception as e:
            log_error(f"[memory] autoload failed: {e}")
            raise RegistryError("Failed to autoload memory backends")

    @classmethod
    def get_active_memory(cls) -> MemoryInterface:
        """Get active memory backend instance based on config."""
        if not cls._registry:
            cls.autoload()

        memory_type = getattr(CurrentConfig, "MEMORY_TYPE", "redis")
        memory_cls = cls.get(memory_type)
        if not memory_cls:
            raise ConfigError(
                f"Memory backend '{memory_type}' not found.",
                context={"available": cls.list()},
            )

        instance = cls.create_instance(memory_type)
        log_info("Active memory backend initialized", backend=memory_type)
        return instance
