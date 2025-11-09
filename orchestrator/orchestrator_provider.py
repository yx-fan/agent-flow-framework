from functools import lru_cache
from orchestrator.impl.orchestrator_impl import OrchestratorImpl
from core.logger import get_logger, log_error
from core.exceptions import MCPRuntimeError

logger = get_logger("OrchestratorProvider")

@lru_cache(maxsize=1)
def get_orchestrator_service() -> OrchestratorImpl:
    """Global singleton provider for the Orchestrator service."""
    try:
        orchestrator = OrchestratorImpl()
        logger.info("Orchestrator instance created successfully.")
        return orchestrator
    except Exception as e:
        log_error("Failed to initialize orchestrator.", error=str(e))
        raise MCPRuntimeError("Failed to initialize orchestrator service.") from e
