import asyncio
from typing import Dict, Any, Optional

from orchestrator.orchestrator_interface import OrchestratorInterface
from orchestrator.agent_router import AgentRouter
from orchestrator.langgraph_builder import LangGraphBuilder
from orchestrator.state_manager import StateManager
from langgraph.graph import StateGraph

from core.logger import get_logger, log_info, log_error, log_warning, log_debug
from core.exceptions import NodeError

logger = get_logger("Orchestrator")


class OrchestratorImpl(OrchestratorInterface):
    """
    Main orchestrator — routes user queries, builds the LangGraph workflow,
    executes it asynchronously, and persists updated session state.
    Supports multi-domain routing (explicitly provided by frontend).
    """

    def __init__(self):
        self.router = AgentRouter()           # pre-load all domain configs
        self.builder = LangGraphBuilder()
        self.state_manager = StateManager()
        log_info("Orchestrator initialized successfully.")

    # ---- main entrypoint ----
    async def handle_user_query(self, session_id: str, query: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Unified entrypoint for user queries.
        Handles pre-processing, intent routing, workflow execution, and persistence.

        Args:
            session_id (str): Unique session identifier
            query (str): User's raw query
            domain (Optional[str]): Domain name (e.g., 'dealer', 'school', etc.)
        """
        log_info("Received user query.", session_id=session_id, query=query, domain=domain or self.router.default_domain)

        try:
            # --- Pre-processing ---
            clean_query = await self.pre_process(query, session_id)
            log_debug("Query pre-processed.", session_id=session_id, clean_query=clean_query)

            # --- Intent routing ---
            route = await self.router.classify_intent(clean_query, domain=domain)
            intent = route.get("intent", "qa")
            resolved_domain = route.get("domain", domain or self.router.default_domain)
            log_info("Intent classified.", session_id=session_id, domain=resolved_domain, intent=intent, method=route.get("method"))

            # --- Run LangGraph workflow ---
            result = await self.run_graph(intent, clean_query, session_id, resolved_domain)
            log_info("Workflow execution complete.", session_id=session_id, domain=resolved_domain, intent=intent)

            # --- Post-processing ---
            final = await self.post_process(result, session_id, resolved_domain)
            log_debug("Post-processing done.", session_id=session_id, domain=resolved_domain)

            # --- Persist updated state ---
            await self.state_manager.save_state(session_id, final)
            log_info("Session state persisted.", session_id=session_id, domain=resolved_domain)

            return {
                "domain": resolved_domain,
                "intent": intent,
                "result": final,
            }

        except Exception as e:
            log_error("Error in orchestrator pipeline.", session_id=session_id, domain=domain, error=str(e))
            return await self.on_error(e, session_id, domain)

    # ---- workflow execution ----
    async def run_graph(self, intent: str, query: str, session_id: str, domain: str) -> Dict[str, Any]:
        """
        Execute a LangGraph workflow for the given intent and domain.
        Responsible for loading state, building the graph, and running it asynchronously.
        """
        try:
            # --- Load prior state ---
            state = await self.state_manager.load_state(session_id)
            log_debug("State loaded for session.", session_id=session_id)

            # --- Build LangGraph workflow ---
            graph = await self.builder.build_graph(intent, domain=domain)
            compiled = graph.compile()
            log_info("LangGraph constructed.", domain=domain, intent=intent, nodes=len(graph.nodes))

            # --- Prepare execution input ---
            inputs = {"query": query, "domain": domain, **state}
            log_debug("Executor inputs prepared.", session_id=session_id, domain=domain)

            # --- Run workflow (async invoke) ---
            result = await compiled.ainvoke(inputs)
            log_info("Graph execution complete.", session_id=session_id, domain=domain, intent=intent)

            # --- Update vector memory (optional) ---
            await self.state_manager.update_memory(session_id, result)

            return result

        except Exception as e:
            log_error("Graph execution failed.", intent=intent, domain=domain, session_id=session_id, error=str(e))
            raise NodeError("Graph execution failed.", context={"intent": intent, "domain": domain, "session": session_id}) from e

    # ---- optional lifecycle hooks ----
    async def pre_process(self, query: str, session_id: str) -> str:
        """Normalize or clean user query before routing."""
        return query.strip()

    async def post_process(self, result: Dict[str, Any], session_id: str, domain: str) -> Dict[str, Any]:
        """Optional hook to refine or enrich workflow output."""
        return result

    async def on_error(self, error: Exception, session_id: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Centralized error handler for graceful fallback."""
        log_error("Pipeline error handled.", session_id=session_id, domain=domain, error=str(error))
        return {
            "status": "error",
            "session_id": session_id,
            "domain": domain or self.router.default_domain,
            "error": str(error),
        }
