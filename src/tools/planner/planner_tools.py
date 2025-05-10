"""Defines tools specifically for the Planner agent."""


def end_planner_turn() -> str:
    """
    A simple function called by the Planner Agent to explicitly end a cycle and send the final response to the user
    or it could after building the final message an ask for more input.
    """
    # This function doesn't need to do much, its execution is the signal.
    # Returning a simple string confirms execution.
    return "--- Planner ended a turn/cycle ---"
