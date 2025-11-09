import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Dict

load_dotenv()


class BaseConfig:
    """Base configuration shared across environments."""

    # ---- General ----
    ENV: str = os.getenv("APP_ENV", "dev")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ---- LLM / API ----
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    RAG_API_URL: str = os.getenv("RAG_API_URL", "http://localhost:8002/api/v1/search")

    # ---- Memory ----
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PREFIX: str = os.getenv("REDIS_PREFIX", "mcp")
    MEMORY_TYPE: str = os.getenv("MEMORY_TYPE", "redis")  # redis | vector | hybrid
    MEMORY_TTL: int = int(os.getenv("MEMORY_TTL", "86400"))  # optional expiration in seconds

    # ---- LangGraph ----
    GRAPH_EXEC_MODE: str = os.getenv("GRAPH_EXEC_MODE", "local")  # local / async / distributed
    GRAPH_MAX_DEPTH: int = int(os.getenv("GRAPH_MAX_DEPTH", "5"))

    # ---- Paths ----
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"

    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Return all config as dictionary (for debugging or introspection)."""
        return {k: getattr(cls, k) for k in dir(cls) if k.isupper()}

    @classmethod
    def summary(cls) -> str:
        """Pretty-print current configuration summary."""
        env = cls.as_dict()
        lines = [f"{k} = {v}" for k, v in env.items()]
        return "\n".join(lines)


# ---- Environment-specific Config ----

class DevConfig(BaseConfig):
    LOG_LEVEL = "DEBUG"
    GRAPH_EXEC_MODE = "local"
    #  Add any other dev-specific overrides here


class ProdConfig(BaseConfig):
    LOG_LEVEL = "INFO"
    GRAPH_EXEC_MODE = "distributed"
    # Add any other prod-specific overrides here


# ---- Active Config Selector ----

def get_config() -> BaseConfig:
    env = os.getenv("APP_ENV", "dev").lower()
    return ProdConfig if env == "prod" else DevConfig


# Alias for global use
CurrentConfig = get_config()
