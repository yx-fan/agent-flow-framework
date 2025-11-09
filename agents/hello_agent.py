# agents/hello_agent.py
from datetime import datetime
from typing import Any, Dict
from core.base_agent import BaseAgent
from providers.llm_service_provider import get_llm_service
from core.logger import log_info, log_error

class HelloAgent(BaseAgent):
    """
    A simple Hello World Agent that demonstrates the BaseAgent lifecycle:
    pre_process → run → post_process
    and calls an LLM provider to generate a cheerful reply.
    """

    name = "HelloAgent"
    description = "A minimal demo agent that calls Azure OpenAI to greet users."

    def __init__(self, memory=None, tools=None):
        super().__init__(memory=memory, tools=tools)
        self.llm = get_llm_service()

    # ---- optional hook overrides ----
    def pre_process(self, query: str, state: Dict[str, Any]) -> str:
        """Normalize or enrich query text before main execution."""
        query = (query or "").strip()
        log_info(f"[{self.name}] pre_process completed.", query=query)
        return query

    def post_process(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Refine and finalize agent output."""
        output["agent"] = self.name
        log_info(f"[{self.name}] post_process completed.")
        return output

    # ---- main async logic ----
    async def run(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent logic (LLM call + response formatting).
        This is the core async execution body.
        """
        timestamp = datetime.utcnow().isoformat()
        log_info(f"[{self.name}] running.", query=query)

        try:
            # --- Call the LLM ---
            prompt = f"You are a friendly assistant. Reply to: '{query}' in a cheerful tone."
            log_info(f"[{self.name}] calling LLM...", prompt_preview=prompt[:80])
            llm_response = await self.llm.apredict(prompt)

            reply = f"👋 Hello! You said: '{query}'.\nLLM says: {llm_response}"

            log_info(f"[{self.name}] got LLM response.", llm_response=llm_response[:100])
            return {
                "reply": reply,
                "timestamp": timestamp,
                "llm_used": True,
            }

        except Exception as e:
            log_error(f"[{self.name}] LLM call failed.", error=str(e))
            return {
                "reply": f"👋 Hello! You said: '{query}', but LLM call failed: {str(e)}",
                "timestamp": timestamp,
                "llm_used": False,
            }
