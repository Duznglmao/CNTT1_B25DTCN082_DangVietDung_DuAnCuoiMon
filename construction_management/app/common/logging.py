import sys
from loguru import logger


def setup_logging() -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", colorize=True)
    logger.add(
        "logs/app.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
    )
