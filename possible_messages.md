# Possible messages to test Planner Agent

# --- Basic Pricing & Clarification ---

1. Can you give me the price for 158 clear vinyl die-cut stickers? the size is 3x3 inches. # Expected: Product ID (30) -> Specific Price -> TASK COMPLETE
2. How much for 200 glow-in-the-dark waterproof sized 4x4 inches? # Expected: Product ID (None) -> Offer Handoff
   2.1 (Follow-up if offered): Yes please. # Expected: Delegate HubSpot Comment -> TASK COMPLETE (Handoff Confirmed)
   2.2 (Follow-up if offered): No thanks. # Expected: Polite acknowledgement -> <UserProxyAgent>
3. Quote for durable roll labels # Expected: Ask for Size & Quantity
   3.1. Sizes are 3x3 and I want 340 units # Expected: Product ID -> Specific Price -> TASK COMPLETE
4. Cost for stickers 3x3? # Expected: Ask for Product Type & Quantity
5. What are the price options for 2x2 kiss-cut stickers? # Expected: Product ID -> Price Tiers -> TASK COMPLETE (Formatted Tiers)

# --- HubSpot Interaction ---

6. Can you send a message to a conversation in hubspot? # Expected: Ask for threadID & message text
   6.1. Yes, the thread is: 9016967488 and please state that we are having issues with the printers that the service will be back online soon # Expected: Delegate send_message_to_thread -> TASK COMPLETE
7. Can you show me the last 3 messages for thread 9016967488? # Expected: Delegate get_thread_messages(limit=3) -> TASK COMPLETE (Summarized messages)

# --- Order Status & Issues ---

8. What is the status of my order 67890? # Expected: Delegate sy_get_order_details -> Extract Status -> TASK COMPLETE (e.g., "Shipped", "In Progress")
9. Can you check order 11111? # Expected: Delegate sy_get_order_details -> Fails (404) -> Delegate HubSpot Comment (Standard Failure) -> TASK FAILED (Inform user of check failure & handoff)

# --- Dissatisfaction Handoff ---

10. My order 12345 is taking forever and I'm really angry! Where is it?! # Expected: Attempt sy_get_order_details -> Extract Status (if any) -> Offer Handoff (due to dissatisfaction)
    10.1 (Follow-up if offered): Yes, have someone call me urgently. # Expected: Delegate HubSpot Comment -> TASK FAILED (Handoff Confirmed)
    10.2 (Follow-up if offered): No, just find my order! # Expected: Polite acknowledgement / Reiterate Status / Cannot proceed -> <UserProxyAgent>

# --- Memory / Context ---

11. Price for 50 3x3 die-cut stickers? # Expected: Product ID (38) -> Specific Price -> TASK COMPLETE
    11.1 (Follow-up in next turn): Okay, what about for 100 of those same stickers? # Expected: Use remembered ID (38) & Size (3x3) -> Specific Price (100) -> TASK COMPLETE

# --- Out of Scope ---

12. Can you tell me the current price for tesla? # Expected: Polite refusal -> <UserProxyAgent>

# --- Developer Mode Tests (-dev prefix required) ---

13. `-dev list the available HubSpot inboxes` # Expected: Delegate list_inboxes -> TASK COMPLETE (Summarized list or raw data)
14. `-dev try to get price for product 999, qty 100, size 1x1` # Simulate non-404 API Error. Expected: Delegate sy_get_specific_price -> Fails (e.g., 500 error) -> Delegate HubSpot Comment (Standard Failure) -> TASK FAILED (Report specific SY_TOOL_FAILED error & handoff)
15. `-dev what was the result of the last SY API call?` # Expected: Planner uses memory/knowledge to answer about previous step.
