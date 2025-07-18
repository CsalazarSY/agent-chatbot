# /src/services/message_to_html.py

import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import LinkInlineProcessor
from src.services.logger_config import log_message
import html


# --- Custom Markdown Extension for Link Styling ---

class BlueLinkExtension(Extension):
    """
    A custom Markdown extension to add a 'link-blue' class to all links.
    """
    def extendMarkdown(self, md):
        # Create a custom inline processor for links
        class BlueLinkProcessor(LinkInlineProcessor):
            def handleMatch(self, m, data):
                el, start, end = super().handleMatch(m, data)
                if el is not None:
                    el.set('class', 'link-blue')
                    el.set('style', 'color: blue;')
                return el, start, end

        # Register the custom processor with a high priority
        md.inlinePatterns.register(BlueLinkProcessor(markdown.inlinepatterns.LINK_RE, md), 'link', 160)


# --- Markdown Converter Setup ---
# We instantiate this once to be reused.
# Extensions:
# - 'nl2br': Converts single newlines ('\n') into <br> tags.
# - 'fenced_code': Handles code blocks correctly.
# - 'tables': For rendering markdown tables.
# - 'sane_lists': For more robust list parsing.
# - BlueLinkExtension(): Our custom extension for blue links.
md_converter = markdown.Markdown(
    extensions=[
        "nl2br",
        "fenced_code",
        "tables",
        "sane_lists",
        BlueLinkExtension(),
    ]
)


async def convert_message_to_html(text_message: str) -> str:
    """
    Uses the 'python-markdown' library to convert a text message (potentially Markdown)
    into an HTML string. This is a direct, fast, and reliable replacement for the
    previous Message Supervisor Agent.

    Args:
        text_message: The raw text message to format.

    Returns:
        The formatted HTML string with blue links.
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