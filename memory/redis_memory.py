import json
import redis.asyncio as aioredis
from typing import Any, Dict, List, Optional
from core.logger import get_logger
from core.exceptions import MemoryError
from core.config import CurrentConfig
from core.memory_interface import MemoryInterface

logger = get_logger("RedisMemory")


class RedisMemory(MemoryInterface):
    """
    Redis-based implementation of MemoryInterface.
    Handles session states, message history, and optional vector memory.
    """

    def __init__(self):
        redis_host = getattr(CurrentConfig, "REDIS_HOST", "localhost")
        redis_port = getattr(CurrentConfig, "REDIS_PORT", 6379)
        redis_db = getattr(CurrentConfig, "REDIS_DB", 0)
        self.prefix = getattr(CurrentConfig, "REDIS_PREFIX", "mcp")

        try:
            self.redis = aioredis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
            logger.info(f"[RedisMemory] Connected to Redis ({redis_host}:{redis_port}, db={redis_db})")
        except Exception as e:
            logger.error(f"[RedisMemory] Failed to connect: {e}")
            raise MemoryError("Unable to connect to Redis") from e

    # ---- State Operations ----
    async def load_state(self, session_id: str) -> Dict[str, Any]:
        """Load full state dict from Redis."""
        try:
            raw = await self.redis.get(f"{self.prefix}:state:{session_id}")
            return json.loads(raw) if raw else {}
        except Exception as e:
            logger.error(f"[RedisMemory] load_state failed: {e}")
            raise MemoryError("Failed to load state") from e

    async def save_state(self, session_id: str, state: Dict[str, Any]):
        """Save workflow state dict."""
        try:
            await self.redis.set(f"{self.prefix}:state:{session_id}", json.dumps(state))
            logger.debug(f"[RedisMemory] Saved state for session={session_id}")
        except Exception as e:
            logger.error(f"[RedisMemory] save_state failed: {e}")
            raise MemoryError("Failed to save state") from e

    async def clear_state(self, session_id: str):
        """Remove all related memory keys."""
        try:
            await self.redis.delete(
                f"{self.prefix}:state:{session_id}",
                f"{self.prefix}:messages:{session_id}",
                f"{self.prefix}:vectors:{session_id}",
            )
            logger.info(f"[RedisMemory] Cleared memory for {session_id}")
        except Exception as e:
            logger.error(f"[RedisMemory] clear_state failed: {e}")

    # ---- Message Operations ----
    async def append_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Append a message to Redis list."""
        try:
            message = {"role": role, "content": content, "metadata": metadata or {}}
            await self.redis.rpush(f"{self.prefix}:messages:{session_id}", json.dumps(message))
        except Exception as e:
            logger.error(f"[RedisMemory] append_message failed: {e}")
            raise MemoryError("Failed to append message") from e

    async def get_messages(self, session_id: str, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
        """Retrieve recent messages."""
        try:
            total = await self.redis.llen(f"{self.prefix}:messages:{session_id}")
            start = max(total - limit, 0)
            items = await self.redis.lrange(f"{self.prefix}:messages:{session_id}", start, total)
            return [json.loads(i) for i in items]
        except Exception as e:
            logger.error(f"[RedisMemory] get_messages failed: {e}")
            raise MemoryError("Failed to get messages") from e

    # ---- Vector Memory (Optional) ----
    async def store_vector(self, session_id: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None):
        """Store embedding and metadata."""
        try:
            entry = json.dumps({"embedding": embedding, "metadata": metadata or {}})
            await self.redis.rpush(f"{self.prefix}:vectors:{session_id}", entry)
        except Exception as e:
            logger.warning(f"[RedisMemory] store_vector skipped: {e}")

    async def search_vector(self, session_id: str, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Placeholder for similarity search (requires vector DB)."""
        logger.debug(f"[RedisMemory] Vector search not implemented yet.")
        return []
