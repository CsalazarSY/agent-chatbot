"""Constants for instructions issued by the Price Quote Agent (PQA) to the Planner Agent"""

# src/agents/pqa_planner_instructions.py

# Constants for instructions issued by the Price Quote Agent (PQA) to the Planner Agent

# Instruction for Planner to ask the user a question
PLANNER_ASK_USER = "PLANNER_ASK_USER"

# Instruction for Planner to acknowledge user has a design file and ask the next question
PLANNER_ACKNOWLEDGE_DESIGN_FILE_AND_PROCEED = (
    "PLANNER_ACKNOWLEDGE_DESIGN_FILE_AND_PROCEED"
)

# Instruction for Planner to acknowledge user wants design assistance, update form_data, and ask the next question
PLANNER_ACKNOWLEDGE_DESIGN_ASSISTANCE_AND_PROCEED = (
    "PLANNER_ACKNOWLEDGE_DESIGN_ASSISTANCE_AND_PROCEED"
)

# Instruction for Planner to acknowledge user does not want design assistance and ask the next question
PLANNER_ACKNOWLEDGE_NO_DESIGN_ASSISTANCE_AND_PROCEED = (
    "PLANNER_ACKNOWLEDGE_NO_DESIGN_ASSISTANCE_AND_PROCEED"
)

# Instruction for Planner to ask the user to confirm the summarized data (PQA provides the summary text)
PLANNER_ASK_USER_FOR_CONFIRMATION = "PLANNER_ASK_USER_FOR_CONFIRMATION"

# Instruction for Planner that custom quote data validation was successful and to proceed with ticket creation
PLANNER_VALIDATION_SUCCESSFUL_PROCEED_TO_TICKET = (
    "PLANNER_VALIDATION_SUCCESSFUL_PROCEED_TO_TICKET"
)

# Instruction for Planner that custom quote data validation failed and to re-ask the user (PQA provides reason/question)
PLANNER_REASK_USER_DUE_TO_VALIDATION_FAILURE = (
    "PLANNER_REASK_USER_DUE_TO_VALIDATION_FAILURE"
)
