# Test Messages for Planner Agent and System

This file contains example messages to test the different functionalities and workflows of the agent system.

**Placeholders:**
*   `[ORDER_ID]` - Replace with a specific StickerYou Order ID for testing.
*   `[DESIGN_ID]` - Replace with a specific StickerYou Design ID (e.g., dz_xxxxx).
*   `[THREAD_ID]` - Replace with a valid HubSpot Thread ID for the conversation.
*   `[MESSAGE_ID]` - Replace with a specific HubSpot Message ID.
*   `[ACTOR_ID]` - Replace with a specific HubSpot Actor ID (e.g., A-xxxxx).
*   `[INBOX_ID]` - Replace with a specific HubSpot Inbox ID.
*   `[DEFAULT_CHANNEL_ACCOUNT_ID]` - The configured default HubSpot channel account ID.
*   `[DEFAULT_SENDER_ACTOR_ID]` - The configured default HubSpot sender actor ID.
---

### Available Test Order IDs (Prod env)

#### Cancelled Status

* `SHO26994` - items: 1

#### Error Status

* `BVO45864` - items: 1
* `MINE44771` - items: 1
* `MINE48173` - items: 1
* `MINE49129` - items: 1
* `WON11274` - items: 1
* `WON18670` - items: 1
---

## Customer Service Scenarios

*(Simulates end-user interactions)*

**1. Success Scenarios (User Expects Result/Confirmation)**

*   **Pricing - Specific Quantity (Direct Flow):**
    * "How much are 500 durable roll labels, 2 inches by 4 inches?"
      * Expected: Planner -> ProductAgent (Find ID) -> ID Found (30) -> Planner -> SYAgent (Get Specific Price) -> Extract Price -> TASK COMPLETE (Price Result)
      
*   **Pricing - Tier Options (Direct Flow):** 
    * "What are the prices for Permanent Holographic 4x4 inch?"
      * Expected: Planner -> ProductAgent (Find ID) -> ID Found (52) -> Planner -> SYAgent (Get Specific Price) -> Extract Price -> TASK COMPLETE (Price Result)

*   **Pricing - Multi-turn Clarification:**
    * "I need a quote for 75 kiss-cut removable vinyl stickers, 3x3 inches."
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'kiss-cut removable vinyl stickers') -> Multiple Matches Found (including 'Removable Smart Save Kiss-Cut Singles').
        2. Planner asks user for clarification -> <UserProxyAgent>.
        3. User clarifies ('Removable Smart Save Kiss-Cut Singles').
        4. Planner -> ProductAgent (Find ID for 'Removable Smart Save Kiss-Cut Singles') -> ID Found (73).
        5. Planner -> SYAgent (Get Specific Price for ID 73, 3x3, Qty 75) -> SY_TOOL_FAILED (Minimum quantity error, e.g., 500).
        6. Planner informs user about minimum quantity and asks for confirmation -> <UserProxyAgent>.
        7. User agrees to minimum quantity.
        8. Planner -> SYAgent (Get Specific Price for ID 73, 3x3, Qty 500) -> Extract Price.
        9. TASK COMPLETE (Price Result for 500 units).

    * "What are the price options for 2x2 kiss-cut stickers?"
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'kiss-cut stickers') -> Multiple Matches Found.
        2. Planner asks user for clarification (listing matches) -> <UserProxyAgent>.
        3. User clarifies (e.g., 'Removable Vinyl Sticker Hand-Outs').
        4. Planner -> ProductAgent (Find ID for clarified description) -> ID Found (11).
        5. Planner -> SYAgent (Get Price Tiers for ID 11, 2x2) -> Extract Tiers.
        6. TASK COMPLETE (Formatted Tiers List).

    * "Show me prices for different quantities of 3x3 die-cut stickers."
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'die-cut stickers') -> Multiple Matches Found.
        2. Planner asks user for clarification (listing matches) -> <UserProxyAgent>.
        3. User clarifies (e.g., 'Permanent Glow In The Dark Glossy').
        4. Planner -> ProductAgent (Find ID for clarified description) -> ID Found (74).
        5. Planner -> SYAgent (Get Price Tiers for ID 74, 3x3) -> Extract Tiers.
        6. TASK COMPLETE (Formatted Tiers List).

    * "I'm not sure how many I need yet. Can you give me pricing tiers for 4x4 removable clear stickers?"
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'removable clear stickers') -> Multiple Matches Found.
        2. Planner asks user for clarification (listing matches and formats) -> <UserProxyAgent>.
        3. User clarifies (e.g., 'Removable Clear Stickers in pages format').
        4. Planner -> ProductAgent (Find ID for clarified description) -> ID Found (2).
        5. Planner -> SYAgent (Get Price Tiers for ID 2, 4x4) -> Extract Tiers.
        6. TASK COMPLETE (Formatted Tiers List, noting stickers per page).

    * "Quote for durable roll labels"
      * Expected (Multi-turn):
         1. Planner -> ProductAgent (Find ID) -> ID Found (30) -> Planner asks user for Size & Quantity -> <UserProxyAgent>
         2. "3x3 and 500 units"
         3. Planner uses context (ID 30) -> SYAgent (Get Specific Price) -> Extract Price -> TASK COMPLETE (Price Result)

*   **Order Status - Found:**
    * "What is the tracking code of my order OQA12346?"
      * Expected: Planner -> SYAgent (Get Order Details) -> Extract Status -> Planner -> SYAgent (Get Tracking) -> Extract Tracking -> TASK COMPLETE (Shipped Status + Tracking)
    
    * "Can you check on my order OQA12345?"
      * Expected: Planner -> SYAgent (Get Order Details) -> Extract Status -> TASK COMPLETE (In Progress Status)

*   **Product Information:**
    * "Which die-cut stickers do you have available?"
      * Expected: Planner -> ProductAgent (List matching 'die-cut') -> Agent returns list -> TASK COMPLETE (Formatted List)
    * "Tell me about the removable clear stickers product."
      * Expected: Planner -> ProductAgent (Find details for 'removable clear stickers') -> Agent returns summary -> TASK COMPLETE (Product Summary)
    * "What kinds of roll labels can I order?"
      * Expected: Planner -> ProductAgent (List matching format 'Rolls') -> Agent returns list -> TASK COMPLETE (Formatted List)
    * "How many types of vinyl stickers do you offer?"
      * Expected: Planner -> ProductAgent (Count matching material 'Vinyl') -> Agent returns count -> TASK COMPLETE (Count Result)

*   **Context / Memory:**
    * "Price for 50 4x4 die-cut stickers?" 
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'die-cut stickers') -> Multiple Matches.
        2. Planner asks for clarification -> <UserProxyAgent>.
        3. User clarifies (e.g., 'Permanent Glow In The Dark Glossy').
        4. Planner -> ProductAgent (Find ID for clarified) -> ID Found (e.g., 74).
        5. Planner -> SYAgent (Get Specific Price ID 74, 4x4, Qty 50) -> Extract Price.
        6. TASK COMPLETE (Price Result).
      * (Follow-up) "Okay, what about 250 of those?" # Expected: Planner uses context (ID 74, size 4x4) -> SYAgent (Get Specific Price for 250) -> Extract Price -> TASK COMPLETE (Price Result)

**2. Failure / Handoff Scenarios (User Encounters Problem)**

*   **Product Not Found:**
    * "How much for 200 transparent paper stickers sized 4x4 inches?"
      * Expected: Planner -> ProductAgent (Find ID) -> Not Found -> Planner -> HubSpotAgent (Send Comment) -> TASK FAILED (Handoff)
    * "Price for polyester stickers?"
      * Expected: Planner -> ProductAgent (Find ID) -> Not Found -> Planner -> HubSpotAgent (Send Comment) -> TASK FAILED (Handoff)

*   **Order Not Found:**
    * "Can you check the status of order OQANovalid21?"
      * Expected: Planner -> SYAgent (Get Order Details) -> SY_TOOL_FAILED (404) -> Planner -> HubSpotAgent (Send Comment) -> TASK FAILED (Handoff)
    * "What's the tracking on order 999999?"
      * Expected: Planner -> SYAgent (Get Order Details or Get Tracking) -> SY_TOOL_FAILED (404) -> Planner -> HubSpotAgent (Send Comment) -> TASK FAILED (Handoff)

*   **SY API Failure (Simulated):**
    * "How much for 100 3x3 die-cut stickers?" *(Requires simulating internal SY API failure -> Standard Failure Handoff)*
      * Expected: Planner -> ProductAgent (Find ID) -> ID Found -> Planner -> SYAgent (Get Specific Price) -> SY_TOOL_FAILED (e.g., Timeout) -> Planner -> HubSpotAgent (Send Comment) -> TASK FAILED (Handoff)

*   **Dissatisfaction:**
    * "My order is taking forever! I'm really angry! Where is it?!" # Expected: Planner -> acknowledge frustratin -> Ask for order ID
      * (Follow-up - Order ID) 893498313
         * Expected: Planner -> SYAgent (Get Order Details) -> Extract Status -> Planner offers handoff -> <UserProxyAgent>
      * (Follow-up - Accept Handoff) "Yes, have someone call me!"
         * Expected: Planner -> HubSpotAgent (Send Comment) -> TASK FAILED (Handoff Confirmed)
      * (Follow-up - Decline Handoff) "No, just find my order!"
         * Expected: Planner acknowledges politely -> <UserProxyAgent>

*   **Out of Scope:**
    * "What's the weather like today?"
      * Expected: Planner politely refuses -> <UserProxyAgent>
    * "Can you help me book a flight?"
      * Expected: Planner politely refuses -> <UserProxyAgent>

*   **Requesting Dev-Only Action:**
    * "Please cancel my order ORD-67890."
      * Expected: Planner explains inability and offers handoff -> <UserProxyAgent>
    * "Can you close my chat thread?"
      * Expected: Planner explains inability and offers handoff -> <UserProxyAgent>

---

## Developer Mode (`-dev`) Scenarios

*(Simulates developer interactions for testing/debugging)*

**1. Success Scenarios (Dev Expects Result/Confirmation)**

*   **Test SY API Tools:**
    * "-dev Get price: product_id=38, width=3, height=3, quantity=555" 
      * Expected: Planner -> SYAgent (Get Specific Price) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev Get price tiers: product_id=30, width=2, height=4" 
      * Expected: Planner -> SYAgent (Get Price Tiers) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev List supported countries" 
      * Expected: Planner -> SYAgent (List Countries) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev Get order details for ORD-12345" 
      * Expected: Planner -> SYAgent (Get Order Details) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev Get tracking for ORD-12345" 
      * Expected: Planner -> SYAgent (Get Tracking) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev Get item statuses for ORD-67890" 
      * Expected: Planner -> SYAgent (Get Item Statuses) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev Get design preview for [DESIGN_ID]" 
      * Expected: Planner -> SYAgent (Get Design Preview) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev List orders via GET with status 30" 
      * Expected: Planner -> SYAgent (List Orders GET) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev List orders via POST: status=50, take=10, skip=5" 
      * Expected: Planner -> SYAgent (List Orders POST) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev Cancel order ORD-67890" *(Use a non-critical/test order)* 
      * Expected: Planner -> SYAgent (Cancel Order) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)

*   **Test HubSpot Tools:**
    * "-dev Send message 'Test dev message' to thread [THREAD_ID]" 
      * Expected: Planner -> HubSpotAgent (Send Message) -> Raw JSON/Confirmation -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Send comment 'COMMENT: Test dev comment' to thread [THREAD_ID]" 
      * Expected: Planner -> HubSpotAgent (Send Comment) -> Raw JSON/Confirmation -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Get details for thread [THREAD_ID]" 
      * Expected: Planner -> HubSpotAgent (Get Thread Details) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Get last 5 messages for thread [THREAD_ID]" 
      * Expected: Planner -> HubSpotAgent (Get Thread Messages, limit=5) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev List OPEN threads from hubspot" 
      * Expected: Planner -> HubSpotAgent (List Threads, status=OPEN) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Get details for actor [ACTOR_ID]" 
      * Expected: Planner -> HubSpotAgent (Get Actor Details) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Get batch details for actors [ACTOR_ID_1], [ACTOR_ID_2]" 
      * Expected: Planner -> HubSpotAgent (Get Actors Batch) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev List inboxes from hubspot" 
      * Expected: Planner -> HubSpotAgent (List Inboxes) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Get details for inbox [INBOX_ID]" 
      * Expected: Planner -> HubSpotAgent (Get Inbox Details) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev List channels" 
      * Expected: Planner -> HubSpotAgent (List Channels) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Get details for channel 1000" 
      * Expected: Planner -> HubSpotAgent (Get Channel Details) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev List channel accounts for channel 1000" 
      * Expected: Planner -> HubSpotAgent (List Channel Accounts) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Get details for channel account [DEFAULT_CHANNEL_ACCOUNT_ID]" 
      * Expected: Planner -> HubSpotAgent (Get Channel Account Details) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Get details for message [MESSAGE_ID] in thread [THREAD_ID]" 
      * Expected: Planner -> HubSpotAgent (Get Message Details) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Get original content for message [MESSAGE_ID] in thread [THREAD_ID]" 
      * Expected: Planner -> HubSpotAgent (Get Original Message Content) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Update thread [THREAD_ID] set status to CLOSED" 
      * Expected: Planner -> HubSpotAgent (Update Thread) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Restore thread [THREAD_ID] from archive" *(Requires setting is_currently_archived=true)* 
      * Expected: Planner -> HubSpotAgent (Update Thread, archived=false, is_archived=true) -> Raw JSON -> TASK COMPLETE (Formatted summary + Raw Result)
    * "-dev Archive thread [THREAD_ID]" 
      * Expected: Planner -> HubSpotAgent (Archive Thread) -> Confirmation String -> TASK COMPLETE (Confirmation String)
    
*   **Test Product Agent Interpretation:**
    * "-dev Find ID for 'removable stickers'"
      * Expected: Planner -> ProductAgent (Find ID) -> Agent returns 'Multiple products match...' string -> TASK COMPLETE (Agent's string)
    * "-dev List products matching format 'Rolls'"
      * Expected: Planner -> ProductAgent (List matching format) -> Agent returns 'Found products matching...' string -> TASK COMPLETE (Agent's string)
    * "-dev How many products use 'Vinyl' material?"
      * Expected: Planner -> ProductAgent (Count matching material) -> Agent returns 'Found N products...' string -> TASK COMPLETE (Agent's string)
    * "-dev Summarize the differences between products matching 'removable stickers'"
      * Expected: Planner -> ProductAgent (Summarize differences) -> Agent returns natural language summary -> TASK COMPLETE (Agent's summary)

*   **Test Planner Internals/Knowledge:**
    * "-dev What was the result of the last SY API call?"
      * Expected: Planner answers based on memory -> TASK COMPLETE (Answer)
    * "-dev Which agent handles pricing?"
      * Expected: Planner answers based on system message -> TASK COMPLETE (Answer: SYAPIAgent)
    * "-dev Explain the standard failure handoff workflow."
      * Expected: Planner explains based on system message -> TASK COMPLETE (Explanation)
    * "-dev What is the configured default SY country code?"
      * Expected: Planner answers based on config -> TASK COMPLETE (Answer: US/Default)

**2. Failure / Handoff Scenarios (Dev Expects Error/Failure Message)**

*   **API Failures:**
    * "-dev Get order details for ORD-NONEXISTENT"
      * Expected: Planner -> SYAgent -> SY_TOOL_FAILED (404) -> TASK FAILED (Reason: SY_TOOL_FAILED...)
    * "-dev Send message 'Test' to thread INVALID_THREAD"
      * Expected: Planner -> HubSpotAgent -> HUBSPOT_TOOL_FAILED (...) -> TASK FAILED (Reason: HUBSPOT_TOOL_FAILED...)
    * "-dev Get price: product_id=9999, width=1, height=1, quantity=1"
      * Expected: Planner -> SYAgent -> SY_TOOL_FAILED (...) -> TASK FAILED (Reason: SY_TOOL_FAILED...)

*   **Agent/Planner Errors:**
    * "-dev Find ID for 'stickers'" *(Requires simulating internal SY API failure)*
      * Expected: Planner -> ProductAgent -> SY_TOOL_FAILED (...) -> TASK FAILED (Reason: SY_TOOL_FAILED...)
    * "-dev Get specific price for product_id=38"
      * Expected: Planner detects missing params -> TASK FAILED (Reason: Error: Missing mandatory parameter...)
    * "-dev Update thread"
      * Expected: Planner detects missing params -> TASK FAILED (Reason: Error: Missing mandatory parameter...)

*   **Invalid Requests:**
    * "-dev Make me a coffee"
      * Expected: Planner reports unclear/out-of-scope -> TASK FAILED (Reason: Request unclear...)
    * "-dev Use the sy_verify_login tool"
      * Expected: Planner checks scope, refuses -> TASK FAILED (Reason: Tool scope [Internal Only]...)

---
