
def log_message(
    message: str,
    level: int = 1,
    prefix: str = "->",
):
    """
    Logs a message with a specified indentation level using the logging module.

    Args:
        message (str): The message to log.
        level (int): The indentation level (1 = no indent, 2 = one indent, etc.).
        log_type (LogLevel): The type of log ('info', 'debug', 'warning', etc.).
        prefix (str): The character to prefix the message with. Defaults to '->'.
    """
    # Calculate indentation. Level 1 has no indent.
    indentation = "  " * (level - 1)

    # Construct and log the final message
    log_string = f"{indentation}{prefix} {message}"
    print(log_string)