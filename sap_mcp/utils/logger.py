import sys
from loguru import logger

def setup_logger():
    """
    Standard logger configuration for the SAP MCP server.
    """
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> <level>{level: <7}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )
    logger.add(
        "logs/adapter.log",
        rotation="10 MB",
        retention="1 week",
        level="INFO"
    )
    return logger
