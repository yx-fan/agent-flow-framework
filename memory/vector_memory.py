from typing import Any, Dict, List
from core.logger import get_logger

logger = get_logger("VectorMemory")


class VectorMemory:
    """
    Placeholder for long-term semantic memory.
    Intended for Milvus / FAISS / Chroma integration.
    """

    def __init__(self):
        logger.info("[VectorMemory] Initialized placeholder backend.")

    async def store_vector(self, session_id: str, embedding: List[float], metadata: Dict[str, Any]):
        logger.debug(f"[VectorMemory] store_vector called for {session_id}")

    async def search_vector(self, session_id: str, query_vector: List[float], top_k: int = 5):
        logger.debug(f"[VectorMemory] search_vector placeholder.")
        return []
