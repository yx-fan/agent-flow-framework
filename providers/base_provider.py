# src/providers/base_provider.py
from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    async def generate(self, *args, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
