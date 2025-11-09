# core/logger.py
import logging
import sys
from datetime import datetime
from core.config import CurrentConfig

def setup_logger(name: str = "mcp", level: str | None = None) -> logging.Logger:
    """Setup a consistent logger for the MCP framework."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level or CurrentConfig.LOG_LEVEL.upper())
    return logger

def get_logger(name: str = "mcp") -> logging.Logger:
    """Alias for setup_logger(name), for consistent external imports."""
    return setup_logger(name)

# ---- Helper functions ----
logger = setup_logger()

def log_debug(message: str, **context):
    logger.debug(_format(message, context))

def log_info(message: str, **context):
    logger.info(_format(message, context))

def log_warning(message: str, **context):
    logger.warning(_format(message, context))

def log_error(message: str, **context):
    logger.error(_format(message, context))

def log_exception(message: str, **context):
    logger.exception(_format(message, context))


# ---- Internal utility ----
def _format(message: str, context: dict) -> str:
    if not context:
        return message
    meta = " | ".join(f"{k}={v}" for k, v in context.items())
    return f"{message} [{meta}]"
