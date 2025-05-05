"""Defines tools specifically for the Planner agent."""


def end_planner_turn() -> str:
    """
    A simple function called by the Planner Agent to explicitly signal
    the end of its processing turn for the current user request.
    Its execution triggers the FunctionCallTermination condition.
    """
    # This function doesn't need to do much, its execution is the signal.
    # Returning a simple string confirms execution.
    return "Planner turn ended."
