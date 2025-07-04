import logging
import sys
from typing import Literal

# Define a type for our log levels for better type hinting
LogLevel = Literal["info", "debug", "warning", "error", "critical"]

def setup_custom_logger():
    """
    Configures the root logger for the application.
    This should be called once when the application starts.
    """
    # Uvicorn and other servers can pre-configure logging.
    # To ensure our format is used, we clear existing handlers
    # and re-configure with basicConfig.
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        stream=sys.stdout,  # Ensure logs go to standard output
    )

def log_message(
    message: str,
    level: int = 1,
    log_type: LogLevel = "info",
    prefix: str = "->",
):
    """
    Logs a message with a specified indentation level.

    Args:
        message (str): The message to log.
        level (int): The indentation level (1 = no indent, 2 = one indent, etc.).
        log_type (LogLevel): The type of log ('info', 'debug', 'warning', etc.).
        prefix (str): The character to prefix the message with. Defaults to '->'.
    """
    # Calculate indentation. Level 1 has no indent.
    indentation = "  " * (level - 1)

    # Get the actual logger function (e.g., logging.info, logging.warning)
    # logger_func = getattr(logging, log_type, logging.info)

    # Construct and log the final message
    log_string = f"{indentation}{prefix} {message}"
    # logger_func(log_string)
    print(log_string)
