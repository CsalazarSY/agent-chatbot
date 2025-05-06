"""Service for cleaning up Planner's final output tags from the agent's response."""

# /src/services/clean_agent_tags.py


# --- Service Functions ---
def clean_agent_output(raw_reply: str) -> str:
    """Clean up Planner's final output tags from the agent's response."""
    cleaned_reply = raw_reply

    # remove task tags
    if cleaned_reply.startswith("TASK COMPLETE"):
        cleaned_reply = cleaned_reply[len("TASK COMPLETE:") :].strip()
    if cleaned_reply.startswith("TASK FAILED"):
        cleaned_reply = cleaned_reply[len("TASK FAILED:") :].strip()

    # remove user proxy tags
    cleaned_reply = cleaned_reply.replace("<UserProxyAgent>", "").strip()
    cleaned_reply = cleaned_reply.replace("<user_proxy>", "").strip()

    # remove potential leading/trailing colons
    if cleaned_reply.startswith(":"):
        cleaned_reply = cleaned_reply[1:].strip()

    return cleaned_reply
