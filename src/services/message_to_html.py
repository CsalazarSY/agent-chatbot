"""Service function to convert plain text/Markdown message to HTML using the python-markdown library."""

# /src/services/message_to_html.py

import markdown
from src.services.logger_config import log_message
import html


# --- Markdown Converter Setup ---
# We instantiate this once to be reused.
# Extensions:
# - 'nl2br': Converts single newlines ('\n') into <br> tags, as specified in our Planner prompt.
# - 'fenced_code': Handles code blocks correctly (e.g., ```python ... ```).
# - 'tables': For rendering markdown tables.
# - 'sane_lists': For more robust list parsing.
md_converter = markdown.Markdown(
    extensions=["nl2br", "fenced_code", "tables", "sane_lists"]
)


async def convert_message_to_html(text_message: str) -> str:
    """
    Uses the 'python-markdown' library to convert a text message (potentially Markdown)
    into an HTML string. This is a direct, fast, and reliable replacement for the
    previous Message Supervisor Agent.

    Args:
        text_message: The raw text message to format.

    Returns:
        The formatted HTML string.
    """
    if not text_message or not text_message.strip():
        return "<p></p>"

    try:
        # The core conversion logic is now a single, synchronous call.
        # We keep the function async to not block the event loop where it's called.
        html_output = md_converter.convert(text_message)

        # After conversion, reset the converter to clear any internal states
        # This is good practice if the server is long-running.
        md_converter.reset()

        log_message(f"HTML Output: {html_output}", prefix="\n\n\n\n\n\n\n\n---", log_type="info", level=1)
        return html_output

    except Exception as e:
        log_message(
            f"EXCEPTION during Markdown to HTML conversion: {e}",
            prefix="!!!",
            log_type="error",
        )
        # Fallback: In case of a very rare error, just wrap the original text in a <p> tag
        # and perform basic HTML escaping to be safe.
        return f"<p>{html.escape(text_message)}</p>"
