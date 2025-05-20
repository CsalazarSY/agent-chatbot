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

### Available Test Order IDs (Prod env) - Note: These are for services OUTSIDE PriceQuoteAgent scope now

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
      * Expected: Planner -> ProductAgent (Find ID) -> ID Found (30) -> Planner -> PriceQuoteAgent (Get Specific Price) -> Extract Price -> TASK COMPLETE (Price Result)
      
*   **Pricing - Tier Options (Direct Flow):** 
    * "What are the prices for Permanent Holographic 4x4 inch?"
      * Expected: Planner -> ProductAgent (Find ID) -> ID Found (52) -> Planner -> PriceQuoteAgent (Get Specific Price) -> Extract Price -> TASK COMPLETE (Price Result)

*   **Pricing - Multi-turn Clarification:**
    * "I need a quote for 75 kiss-cut removable vinyl stickers, 3x3 inches."
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'kiss-cut removable vinyl stickers') -> Multiple Matches Found (including 'Removable Smart Save Kiss-Cut Singles').
        2. Planner asks user for clarification -> <UserProxyAgent>.
        3. User clarifies ('Removable Smart Save Kiss-Cut Singles').
        4. Planner -> ProductAgent (Find ID for 'Removable Smart Save Kiss-Cut Singles') -> ID Found (73).
        5. Planner -> PriceQuoteAgent (Get Specific Price for ID 73, 3x3, Qty 75) -> SY_TOOL_FAILED (Minimum quantity error, e.g., 500).
        6. Planner informs user about minimum quantity and asks for confirmation -> <UserProxyAgent>.
        7. User agrees to minimum quantity.
        8. Planner -> PriceQuoteAgent (Get Specific Price for ID 73, 3x3, Qty 500) -> Extract Price.
        9. TASK COMPLETE (Price Result for 500 units).

    * "What are the price options for 2x2 kiss-cut stickers?"
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'kiss-cut stickers') -> Multiple Matches Found.
        2. Planner asks user for clarification (listing matches) -> <UserProxyAgent>.
        3. User clarifies (e.g., 'Removable Vinyl Sticker Hand-Outs').
        4. Planner -> ProductAgent (Find ID for clarified description) -> ID Found (11).
        5. Planner -> PriceQuoteAgent (Get Price Tiers for ID 11, 2x2) -> Extract Tiers.
        6. TASK COMPLETE (Formatted Tiers List).

    * "Show me prices for different quantities of 3x3 die-cut stickers."
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'die-cut stickers') -> Multiple Matches Found.
        2. Planner asks user for clarification (listing matches) -> <UserProxyAgent>.
        3. User clarifies (e.g., 'Permanent Glow In The Dark Glossy').
        4. Planner -> ProductAgent (Find ID for clarified description) -> ID Found (74).
        5. Planner -> PriceQuoteAgent (Get Price Tiers for ID 74, 3x3) -> Extract Tiers.
        6. TASK COMPLETE (Formatted Tiers List).

    * "I'm not sure how many I need yet. Can you give me pricing tiers for 4x4 removable clear stickers?"
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'removable clear stickers') -> Multiple Matches Found.
        2. Planner asks user for clarification (listing matches and formats) -> <UserProxyAgent>.
        3. User clarifies (e.g., 'Removable Clear Stickers in pages format').
        4. Planner -> ProductAgent (Find ID for clarified description) -> ID Found (2).
        5. Planner -> PriceQuoteAgent (Get Price Tiers for ID 2, 4x4) -> Extract Tiers.
        6. TASK COMPLETE (Formatted Tiers List, noting stickers per page).

    * "Quote for durable roll labels"
      * Expected (Multi-turn):
         1. Planner -> ProductAgent (Find ID) -> ID Found (30) -> Planner asks user for Size & Quantity -> <UserProxyAgent>
         2. "3x3 and 500 units"
         3. Planner uses context (ID 30) -> PriceQuoteAgent (Get Specific Price) -> Extract Price -> TASK COMPLETE (Price Result)

*   **Order Status / Tracking (Feature in Development):**
    * "What is the tracking code of my order OQA12346?"
      * Expected: Planner informs feature is in development, offers ticket -> `<UserProxyAgent>`. (User might accept/decline handoff in next turn).
    * "Can you check on my order OQA12345?"
      * Expected: Planner informs feature is in development, offers ticket -> `<UserProxyAgent>`. (User might accept/decline handoff in next turn).

*   **Product Information:**
    * "Which die-cut stickers do you have available?"
      * Expected: Planner -> ProductAgent (List matching 'die-cut') -> Agent returns list -> TASK COMPLETE (Formatted List)
    * "Tell me about the removable clear stickers product."
      * Expected: Planner -> ProductAgent (Find details for 'removable clear stickers') -> Agent returns summary -> TASK COMPLETE (Product Summary)
    * "What kinds of roll labels can I order?"
      * Expected: Planner -> ProductAgent (List matching format 'Rolls') -> Agent returns list -> TASK COMPLETE (Formatted List)
    * "How many types of vinyl stickers do you offer?"
      * Expected: Planner -> ProductAgent (Count matching material 'Vinyl') -> Agent returns count -> TASK COMPLETE (Count Result)

*   **Context / Memory (Pricing Focus):**
    * "Price for 50 4x4 die-cut stickers?" 
      * Expected (Multi-turn):
        1. Planner -> ProductAgent (Find ID for 'die-cut stickers') -> Multiple Matches.
        2. Planner asks for clarification -> <UserProxyAgent>.
        3. User clarifies (e.g., 'Permanent Glow In The Dark Glossy').
        4. Planner -> ProductAgent (Find ID for clarified) -> ID Found (e.g., 74).
        5. Planner -> PriceQuoteAgent (Get Specific Price ID 74, 4x4, Qty 50) -> Extract Price.
        6. TASK COMPLETE (Price Result).
      * (Follow-up) "Okay, what about 250 of those?" # Expected: Planner uses context (ID 74, size 4x4) -> PriceQuoteAgent (Get Specific Price for 250) -> Extract Price -> TASK COMPLETE (Price Result)

**2. Failure / Handoff Scenarios (User Encounters Problem)**

*   **Product Not Found (Pricing context):**
    * "How much for 200 transparent paper stickers sized 4x4 inches?"
      * Expected: Planner -> ProductAgent (Find ID) -> Not Found -> Planner offers handoff -> TASK FAILED (Handoff offered/initiated)
    * "Price for polyester stickers?"
      * Expected: Planner -> ProductAgent (Find ID) -> Not Found -> Planner offers handoff -> TASK FAILED (Handoff offered/initiated)

*   **Order Not Found (When Inquiring about Status/Tracking - Feature in Development):**
    * "Can you check the status of order OQANovalid21?"
      * Expected: Planner informs feature (order status/tracking) is in development, even if an order ID is provided. Offers ticket -> `<UserProxyAgent>`.

*   **PriceQuoteAgent API Failure (Simulated for Pricing):**
    * "How much for 100 3x3 die-cut stickers?" *(Requires simulating internal PriceQuoteAgent API failure for pricing -> Standard Failure Handoff)*
      * Expected: Planner -> ProductAgent (Find ID) -> ID Found -> Planner -> PriceQuoteAgent (Get Specific Price) -> SY_TOOL_FAILED (e.g., Timeout) -> Planner offers handoff -> TASK FAILED (Handoff offered/initiated)

*   **Dissatisfaction:**
    * "Your website is confusing for prices! I'm really angry!" # Expected: Planner -> acknowledge frustration -> Ask if they need help with a specific quote
      * (Follow-up - if user provides product for quote that leads to error) e.g. "Quote for 10 non-existent stickers"
         * Expected: Planner -> ProductAgent (Find ID) -> Not Found -> Planner explains inability to find product, offers handoff -> <UserProxyAgent>
      * (Follow-up - Accept Handoff) "Yes, have someone help me!"
         * Expected: Planner -> Asks for email -> User provides email -> HubSpotAgent (Create Ticket) -> TASK FAILED (Handoff Confirmed)
      * (Follow-up - Decline Handoff) "No, I'll figure it out!"
         * Expected: Planner acknowledges politely -> <UserProxyAgent>

*   **Out of Scope:**
    * "What's the weather like today?"
      * Expected: Planner politely refuses -> <UserProxyAgent>
    * "Can you help me book a flight?"
      * Expected: Planner politely refuses -> <UserProxyAgent>

*   **Requesting Dev-Only Action:**
    * "Please cancel my order ORD-67890."
      * Expected: Planner states it cannot perform order cancellations (as no agent has this tool now) and that order management features like this are generally under review/development. Offers to create a ticket for the request.

---

## Developer Mode (`-dev`) Scenarios

*(Simulates developer interactions for testing/debugging)*

**1. Success Scenarios (Dev Expects Result/Confirmation)**

*   **Test PriceQuoteAgent Tools (Pricing Focused):**
    * "-dev Get price: product_id=38, width=3, height=3, quantity=555" 
      * Expected: Planner -> PriceQuoteAgent (Get Specific Price) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev Get price tiers: product_id=30, width=2, height=4" 
      * Expected: Planner -> PriceQuoteAgent (Get Price Tiers) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev List supported countries" 
      * Expected: Planner -> PriceQuoteAgent (List Countries) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)
    * "-dev Verify login status"
      * Expected: Planner -> PriceQuoteAgent (sy_verify_login) -> Raw JSON Result -> TASK COMPLETE (Formatted summary + Raw JSON)

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
    * "-dev What was the result of the last PriceQuoteAgent API call?"
      * Expected: Planner answers based on memory -> TASK COMPLETE (Answer)
    * "-dev Which agent handles pricing?"
      * Expected: Planner answers based on system message -> TASK COMPLETE (Answer: PriceQuoteAgent)
    * "-dev Explain the standard failure handoff workflow."
      * Expected: Planner explains based on system message -> TASK COMPLETE (Explanation)
    * "-dev What is the configured default SY country code?"
      * Expected: Planner answers based on config -> TASK COMPLETE (Answer: US/Default)

*   **Test "Feature in Development" Workflows (Order/Tracking):**
    *   "-dev What is the tracking for order SY123?"
        *   Expected: Planner responds with `TASK FAILED: This feature (Direct Tracking Code Request) is currently marked as 'in development'. No agent is assigned to handle this directly in the current configuration. <{USER_PROXY_AGENT_NAME}>`
    *   "-dev What is the status of my order ORD456?"
        *   Expected: Planner responds with `TASK FAILED: This feature (Order Status Check) is currently marked as 'in development'. No agent is assigned to handle this directly in the current configuration. <{USER_PROXY_AGENT_NAME}>`

**2. Failure / Handoff Scenarios (Dev Expects Error/Failure Message)**

*   **API Failures (Pricing Context):**
    * "-dev Get price: product_id=99999, width=1, height=1, quantity=100" *(Simulating a non-existent product ID for pricing)*
      * Expected: Planner -> PriceQuoteAgent (Get Specific Price) -> SY_TOOL_FAILED (e.g., Product not found) -> TASK FAILED (Raw error from PriceQuoteAgent)

*   **Tool Parameter Errors (Pricing Context):**
    * "-dev Get price: product_id=38, quantity=50"
      * Expected: Planner -> PriceQuoteAgent (Get Specific Price) -> Error: Missing mandatory parameter(s)... -> TASK FAILED (Raw error from PriceQuoteAgent)

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