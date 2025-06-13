"""Constants for instructions issued by the Price Quote Agent (PQA) to the Planner Agent"""

# src/agents/instructions_constants.py

# Constants for instructions issued by the Price Quote Agent (PQA) to the Planner Agent

# Instruction for Planner to ask the user a question (can be general, for clarification, or re-asking after validation failure)
PLANNER_ASK_USER = "PLANNER_ASK_USER"

# Instruction for Planner to ask the user to confirm the summarized data (PQA provides the summary text)
PLANNER_ASK_USER_FOR_CONFIRMATION = "PLANNER_ASK_USER_FOR_CONFIRMATION"

# Instruction for Planner that custom quote data validation was successful and to proceed with ticket creation
# PQA will also provide the final form_data object with this instruction.
PLANNER_VALIDATION_SUCCESSFUL_PROCEED_TO_TICKET = (
    "PLANNER_VALIDATION_SUCCESSFUL_PROCEED_TO_TICKET"
)
