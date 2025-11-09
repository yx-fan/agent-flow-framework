from functools import lru_cache
from memory.redis_memory import RedisMemory
from core.logger import get_logger
from core.exceptions import MemoryError

logger = get_logger("MemoryProvider")

@lru_cache(maxsize=1)
def get_memory_service() -> RedisMemory:
    """Singleton provider for RedisMemory instance."""
    try:
        memory = RedisMemory()
        logger.info("RedisMemory initialized successfully.")
        return memory
    except Exception as e:
        logger.error(f"Failed to initialize RedisMemory: {e}")
        raise MemoryError("Failed to initialize RedisMemory") from e
