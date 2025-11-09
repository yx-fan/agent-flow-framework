# src/providers/azure_openai_provider.py
import os
import traceback
from providers.base_provider import BaseLLMProvider
from providers.configs.openai_config import azure_url_lookup
from providers.utils.openai_client import post_openai_chat
from core.logger import get_logger

logger = get_logger("AzureOpenAIProvider")


class AzureOpenAIProvider(BaseLLMProvider):
    """LLM provider for Azure OpenAI Service (multi-deployment support)."""

    def __init__(self):
        self.default_model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("Missing Azure OpenAI API key in environment variables.")

        logger.info(f"[AzureOpenAIProvider] Initialized [default_model={self.default_model}]")

    # ---- Core Chat Interface ----
    async def generate(
        self,
        messages: list[dict],
        system_prompt: str = None,
        stop_sequences: list[str] = None,
        max_tokens: int = 1024,
        reasoning_effort: str = "auto",
        model: str = None,
    ) -> str:
        """Generate response from Azure OpenAI."""
        model = model or self.default_model
        endpoint = azure_url_lookup.get(model)

        if not endpoint:
            logger.error(f"[AzureOpenAIProvider] No endpoint found for model: {model}")
            raise ValueError(f"Azure endpoint not found for model: {model}")

        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "messages": messages,
            "max_completion_tokens": max_tokens,
            "model": model,
        }

        # Support for reasoning models (e.g., o3, o4)
        if "o3" in model or "o4" in model:
            payload["reasoning_effort"] = reasoning_effort
        if stop_sequences:
            payload["stop"] = stop_sequences

        logger.info(f"[AzureOpenAIProvider] Calling model={model} [endpoint={endpoint}]")

        try:
            result = await post_openai_chat(endpoint, self.api_key, payload)
            logger.info(f"[AzureOpenAIProvider] Azure OpenAI call succeeded [model={model}]")
            return result

        except Exception as e:
            logger.error(
                f"[AzureOpenAIProvider] Azure OpenAI call failed [model={model} | error={str(e)}]"
            )
            logger.debug(traceback.format_exc())
            raise

    # ---- Lightweight alias for agents ----
    async def apredict(self, prompt: str, model: str = None) -> str:
        """
        Async predict helper for simple one-shot text prompts.
        Used by agents like HelloAgent.
        """
        try:
            model = model or self.default_model
            logger.info(
                f"[AzureOpenAIProvider] apredict() called [model={model} | prompt_preview={prompt[:80]}]"
            )

            messages = [{"role": "user", "content": prompt}]
            result = await self.generate(messages=messages, model=model)

            logger.info(f"[AzureOpenAIProvider] apredict() succeeded [model={model}]")
            return result

        except Exception as e:
            logger.error(f"[AzureOpenAIProvider] apredict() failed [error={str(e)}]")
            logger.debug(traceback.format_exc())
            raise
