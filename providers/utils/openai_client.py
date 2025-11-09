# providers/utils/openai_client.py
import httpx
from core.logger import get_logger, log_info, log_error, log_debug

logger = get_logger("OpenAIClient")

async def post_openai_chat(url: str, api_key: str, payload: dict) -> str:
    """Send a chat completion request to Azure OpenAI."""
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    try:
        log_debug("Sending OpenAI chat request.", url=url)

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            log_info("OpenAI chat response received.", status=resp.status_code)
            return content

    except httpx.RequestError as e:
        log_error("OpenAI request connection failed.", url=url, error=str(e))
        raise

    except httpx.HTTPStatusError as e:
        log_error(
            "OpenAI returned non-200 status.",
            url=url,
            status=e.response.status_code,
            body=e.response.text,
        )
        raise

    except Exception as e:
        log_error("Unexpected error during OpenAI chat call.", error=str(e))
        raise
