# providers/llm_service_provider.py
import os
from functools import lru_cache
from providers.azure_openai_provider import AzureOpenAIProvider
from core.logger import get_logger, log_error
from core.exceptions import MCPRuntimeError

logger = get_logger("LLMServiceProvider")


@lru_cache(maxsize=1)
def get_llm_service():
    """
    Global singleton provider for the LLM service.
    Returns a cached LLM provider instance (e.g., Azure OpenAI).
    """
    provider_name = os.getenv("LLM_PROVIDER", "azure").lower()
    logger.info(f"Initializing LLM provider: {provider_name}")

    try:
        if provider_name == "azure":
            service = AzureOpenAIProvider()
            logger.info("Azure OpenAI LLM provider initialized successfully.")
            return service

        # future extension:
        # elif provider_name == "openai": ...
        # elif provider_name == "anthropic": ...
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {provider_name}")

    except Exception as e:
        log_error("Failed to initialize LLM provider.", provider=provider_name, error=str(e))
        raise MCPRuntimeError(f"Failed to initialize LLM provider '{provider_name}'") from e
