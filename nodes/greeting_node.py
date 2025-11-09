# nodes/greeting_node.py
from core.base_node import BaseNode
from core.logger import log_info, log_error
from agents.hello_agent import HelloAgent


class GreetingNode(BaseNode):
    """
    Greeting node that greets the user and optionally calls an injected Agent
    (defaults to HelloAgent).
    """

    name = "GreetingNode"
    description = "Handles greeting messages and invokes an Agent for LLM response"
    node_type = "node"

    def __init__(self, agent=None):
        super().__init__(agent=agent or HelloAgent())

    async def execute(self, state: dict) -> dict:
        query = (state.get("query") or "").strip()
        log_info(f"[{self.name}] executing.", query=query)

        # ---- Step 1: Rule-based greeting ----
        if any(word in query.lower() for word in ["hi", "hello", "hey", "morning"]):
            greeting = "Hello there 👋! Let me think about that for you..."
        elif any(word in query.lower() for word in ["bye", "goodbye", "see you"]):
            greeting = "Goodbye! Have a great day ahead 👋"
            return {"query": query, "response": greeting}
        else:
            greeting = f"You said: {query}"

        # ---- Step 2: Call injected Agent ----
        try:
            # ✅ Pass both query and full state
            agent_result = await self.agent.run(query, state)
            log_info(f"[{self.name}] successfully called {self.agent.__class__.__name__}.", query=query)

            # Merge outputs
            return {
                **state,
                "query": query,
                "greeting": greeting,
                "agent_reply": agent_result.get("reply"),
                "timestamp": agent_result.get("timestamp"),
                "llm_used": agent_result.get("llm_used", False),
            }

        except Exception as e:
            log_error(f"[{self.name}] failed to call {self.agent.__class__.__name__}.", error=str(e))
            return {
                **state,
                "query": query,
                "greeting": greeting,
                "error": str(e),
                "llm_used": False,
            }
