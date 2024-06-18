import os
import sys
from loguru import logger


LOGGER_FORMAT = (
    "<cyan>{time:HH:mm:ss.SSS}</cyan> "
    "<light-black>[{thread.name}]</light-black> "
    "<level>[{level}]</level> "
    "<magenta>{function}</magenta> - {message}"
)


def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format=LOGGER_FORMAT,
    )
    logger.level("INFO", color="<blue>")
    logger.level("DEBUG", color="<green>")
