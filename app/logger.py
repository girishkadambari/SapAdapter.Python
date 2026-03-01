# /Users/girish/girish-workspace/sap-copilot-main/SapAdapter.Python/app/logger.py
import sys
from loguru import logger

def setup_logger():
    logger.remove()
    # Console color log
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> <level>{level: <7}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )
    # File rotation log
    logger.add(
        "logs/adapter.log",
        rotation="10 MB",
        retention="1 week",
        level="INFO"
    )
    return logger
