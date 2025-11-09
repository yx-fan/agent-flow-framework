from typing import Dict, Any
import json
from core.logger import get_logger, log_error
from core.exceptions import NodeError
from providers.llm_service_provider import get_llm_service

logger = get_logger("ReflectionNode")


class ReflectionNode:
    """
    ReflectionNode: evaluates AI answers for quality and correctness.
    Built for integration into LangGraph as a self-evaluation node.
    """

    def __init__(self):
        self.llm = get_llm_service()

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate AI output and decide whether to re-ask or proceed.
        Expected inputs:
        {
          "query": "...",
          "previous_output": "..." (or "answer")
        }
        """
        query = inputs.get("query", "")
        answer = inputs.get("previous_output", "") or inputs.get("answer", "")

        if not answer:
            logger.warning("No answer found — skipping reflection.", query=query)
            return {"decision": "ok", "score": 1.0, "comment": "No answer to review."}

        # ---- Build Review Prompt ----
        review_prompt = f"""
        You are a strict evaluator of AI responses.

        Evaluate the assistant's answer for the given question.

        Question: {query}
        Answer: {answer}

        Return JSON:
        {{
          "score": float (0.0 - 1.0),
          "decision": "ok" or "reask",
          "comment": "Explain your reasoning in one line."
        }}
        """

        # ---- LLM Evaluation ----
        try:
            raw = await self.llm.apredict(review_prompt)
            parsed = self._safe_parse(raw)
        except Exception as e:
            log_error("Reflection evaluation failed.", error=str(e), query=query)
            raise NodeError("Reflection LLM evaluation failed.", context={"query": query}) from e

        # ---- Decision Handling ----
        if parsed.get("decision") == "reask":
            clarification = await self._generate_clarification(query)
            result = {
                "decision": "reask",
                "clarify_question": clarification,
                "score": parsed.get("score", 0.6),
                "comment": parsed.get("comment", ""),
            }
            logger.info("Reask triggered.", query=query, clarify_question=clarification)
            return result

        # ---- Normal Path ----
        result = {
            "decision": "ok",
            "score": parsed.get("score", 0.9),
            "comment": parsed.get("comment", ""),
        }
        logger.info("Reflection complete.", query=query, score=result["score"])
        return result

    # ---- Helpers ----
    async def _generate_clarification(self, query: str) -> str:
        """Generate a follow-up question for clarification."""
        clarify_prompt = f"Generate a short follow-up question to clarify: {query}"
        try:
            clarification = await self.llm.apredict(clarify_prompt)
            return clarification.strip()
        except Exception:
            log_error("Clarification generation failed.", query=query)
            return f"Could you clarify your question about: {query}?"

    def _safe_parse(self, raw: Any) -> Dict[str, Any]:
        """Safely parse the LLM output into JSON."""
        if isinstance(raw, dict):
            return raw

        text = str(raw).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Non-JSON response received.", raw=text)
            return {
                "score": 0.8,
                "decision": "ok",
                "comment": "Could not parse; assumed OK.",
            }
