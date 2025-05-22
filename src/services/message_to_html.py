"""Service function to convert plain text/Markdown message to HTML using the Message Supervisor Agent."""

# /src/services/message_to_html.py

import traceback

# Agent Service and Supervisor Agent
from src.agents.agents_services import AgentService  # To access shared model client
from src.agents.message_supervisor.message_supervisor_agent import (
    create_message_supervisor_agent,
)


async def convert_message_to_html(text_message: str) -> str:
    """
    Uses the Message Supervisor Agent to convert a text message (potentially Markdown)
    into an HTML string.

    Args:
        text_message: The raw text message to format.

    Returns:
        The formatted HTML string, or the original text message if formatting fails.
    """
    if not text_message:  # Handle empty input
        return "<p></p>"

    formatted_html = text_message  # Default to original text

    try:
        # Use the secondary model client from the shared AgentService state
        if AgentService.secondary_model_client:
            supervisor_agent = create_message_supervisor_agent()

            supervisor_result = await supervisor_agent.run(task=text_message)

            if supervisor_result and supervisor_result.messages:
                # The supervisor should return only the HTML string as the last message content
                supervisor_final_message = supervisor_result.messages[-1]
                if (
                    hasattr(supervisor_final_message, "content")
                    and isinstance(supervisor_final_message.content, str)
                    and supervisor_final_message.content.strip()  # Ensure not empty string
                ):
                    formatted_html = supervisor_final_message.content
                else:
                    print(
                        "    !!! WARN: (HTML Service) Supervisor agent did not return expected string content."
                    )
            else:
                print(
                    "    !!! WARN: (HTML Service) Supervisor agent failed to produce a result."
                )
        else:
            print(
                "    !!! WARN: (HTML Service) Secondary model client not available for supervisor agent."
            )

    except Exception as supervisor_exc:
        print(
            f"!!! EXCEPTION during Supervisor Agent execution (HTML Service): {supervisor_exc}"
        )
        traceback.print_exc()
        # Fallback to original text is handled by default assignment

    # Basic check to ensure some HTML structure if formatting happened
    # If it still looks like plain text, wrap it in <p>
    if formatted_html == text_message and not formatted_html.strip().startswith("<"):
        formatted_html = f"<p>{formatted_html}</p>"
    elif not formatted_html.strip():  # Handle case where supervisor returns empty
        formatted_html = "<p></p>"

    return formatted_html
