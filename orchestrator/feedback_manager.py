from typing import Dict, Any, Optional, Callable
from datetime import datetime
from core.logger import get_logger, log_info, log_error, log_debug, log_warning
from core.exceptions import NodeError

logger = get_logger("FeedbackManager")


class FeedbackManager:
    """
    Collects feedback from reflection nodes, users, or system metrics.
    Usually placed after ReflectionNode or final output.
    """

    def __init__(self, persist_func: Optional[Callable] = None):
        """
        :param persist_func: optional custom persistence function (e.g., DB insert, analytics API)
        """
        self.persist_func = persist_func
        log_info("FeedbackManager initialized.", has_persistence=bool(persist_func))

    async def collect_feedback(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collects and logs feedback.
        Expected input keys:
        {
            "session_id": str,
            "decision": "ok" | "reask" | "error",
            "score": float,
            "comment": str,
            "source": "human" | "system" | "reflection"
        }
        """
        session_id = inputs.get("session_id", "unknown")
        decision = inputs.get("decision", "ok")
        score = float(inputs.get("score", 0.8))
        comment = inputs.get("comment", "")
        source = inputs.get("source", "system")

        feedback_entry = {
            "session_id": session_id,
            "decision": decision,
            "score": score,
            "comment": comment,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # ---- Log feedback ----
        log_info(
            "Feedback collected.",
            session_id=session_id,
            source=source,
            decision=decision,
            score=score,
            comment=comment,
        )

        # ---- Optional persistence ----
        if self.persist_func:
            try:
                await self._persist_async(feedback_entry)
                log_debug("Feedback persisted successfully.", session_id=session_id)
            except Exception as e:
                log_error("Failed to persist feedback.", session_id=session_id, error=str(e))
                raise NodeError("Failed to persist feedback.", context=feedback_entry) from e
        else:
            log_debug("No persistence function configured; skipping DB write.", session_id=session_id)

        # ---- Auto adjustment ----
        next_action = self._decide_next_action(decision, score)
        log_debug("Feedback processed.", session_id=session_id, next_action=next_action)

        return {
            "status": "recorded",
            "next_action": next_action,
            "feedback": feedback_entry,
        }

    # ---- Internal helper methods ----
    async def _persist_async(self, feedback_entry: Dict[str, Any]):
        """Optional async persistence hook."""
        if callable(self.persist_func):
            result = self.persist_func(feedback_entry)
            if hasattr(result, "__await__"):
                await result  # async persistence
            return result
        else:
            log_warning("Persistence function is not callable.", feedback_entry=feedback_entry)

    def _decide_next_action(self, decision: str, score: float) -> str:
        """
        Simple heuristic: determine the next orchestration action.
        """
        if decision == "reask" or score < 0.5:
            return "retry"
        elif 0.5 <= score < 0.8:
            return "review"
        else:
            return "proceed"
