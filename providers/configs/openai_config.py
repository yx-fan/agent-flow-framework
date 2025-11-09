# src/providers/configs/openai_config.py
import os

# Azure OpenAI endpoints mapped by model name
azure_url_lookup = {
    "gpt-4o": f"{os.getenv('AZURE_OPENAI_ENDPOINT')}/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview",
    "gpt-4.1-mini": f"{os.getenv('AZURE_OPENAI_ENDPOINT')}/openai/deployments/gpt-4.1-mini/chat/completions?api-version=2025-01-01-preview",
}
