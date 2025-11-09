import uuid
from orchestrator.orchestrator_provider import get_orchestrator_service
from core.logger import log_info, log_error

class ChatController:
    def __init__(self):
        self.orchestrator = get_orchestrator_service()

    async def handle_chat(self, session_id: str | None, query: str, domain: str | None = None):
        """
        Handle chat requests by routing them to the orchestrator.
        Automatically generates a session_id if missing.
        Optional `domain` allows routing to different intent sets (e.g. dealer, hello, school).
        """

        # ---- Session ID handling ----
        if not session_id:
            session_id = str(uuid.uuid4())
            log_info("Generated new session_id.", session_id=session_id)

        # ---- Default domain ----
        domain = domain or "hello"

        try:
            # Pass domain to orchestrator
            result = await self.orchestrator.handle_user_query(session_id, query, domain=domain)
            log_info("Chat handled successfully.", session_id=session_id, domain=domain)

            return {
                "session_id": session_id,
                "query": query,
                "domain": domain,
                "result": result,
                "status": "success",
            }

        except Exception as e:
            log_error("Error handling chat.", session_id=session_id, domain=domain, error=str(e))
            return {
                "session_id": session_id,
                "query": query,
                "domain": domain,
                "error": str(e),
                "status": "error",
            }
