## Codebase Summary

This project implements a multi-agent chatbot system using AutoGen, designed to handle customer inquiries related to StickerYou products, pricing, and order management, as well as interactions with HubSpot conversations. The system is exposed via a FastAPI backend.

### 1. Overall Architecture

The system revolves around a set of specialized agents orchestrated by a central **Planner Agent**. User interactions are typically received via a FastAPI endpoint (`/chat` or `/hubspot/webhooks`). The Planner Agent interprets the user's intent, delegates tasks to the appropriate specialist agents, processes their responses, and formulates a final reply. State management across turns within a conversation is handled by the `AgentService`.

### 2. Core Components

*   **`main_server.py`**:
    *   Entry point for the FastAPI application.
    *   Defines API endpoints:
        *   `/chat`: For direct chat interactions.
        *   `/hubspot/webhooks`: To receive and process HubSpot webhook notifications (e.g., new messages).
    *   Manages the application lifecycle (`lifespan` context manager), including an initial StickerYou API token refresh.
    *   Configures CORS for frontend communication.
    *   Uses background tasks for processing HubSpot webhook events asynchronously.
*   **`main.py`**:
    *   Provides a Command Line Interface (CLI) for interacting with the agent system, primarily for testing and development.
    *   Manages a chat loop, taking user input and displaying agent responses.
*   **`config.py`**:
    *   Loads environment variables from a `.env` file using `python-dotenv`.
    *   Validates essential configurations (API base URLs, keys, model names).
    *   Manages the StickerYou API token, including functions to get and set the dynamic token (`get_sy_api_token`, `set_sy_api_token`).
    *   Initializes the HubSpot API client (`HUBSPOT_CLIENT`).
    *   Stores default values for country codes, currency codes, and HubSpot channel/actor IDs.
*   **`environment.yml`**:
    *   Defines Conda environment specifications, listing all Python package dependencies required for the project (e.g., `autogen-agentchat`, `fastapi`, `uvicorn`, `hubspot-api-client`, `pydantic`).

### 3. Agents (`src/agents/`)

The agent layer is responsible for the conversational logic and task execution.

*   **`agents_services.py`**:
    *   Contains the `AgentService` class, which is central to managing agent interactions.
    *   **Shared State**: Initializes and holds shared resources like the `OpenAIChatCompletionClient` and `conversation_states` (an in-memory dictionary to store the state of different conversations).
    *   **Agent Creation**: Dynamically creates instances of all agents (Planner, HubSpot, StickerYou API, Product) for each request, injecting necessary memory and model clients.
    *   **Chat Session Management**: The `run_chat_session` method orchestrates the interaction within a `SelectorGroupChat`. It handles loading and saving conversation state.
    *   **Custom Speaker Selection**: Implements `custom_speaker_selector` logic to determine the next agent to speak based on the conversation history and message content, ensuring a structured flow (e.g., Planner processes specialist agent output, specialist agent responds to Planner's delegation).
    *   **Termination Conditions**: Defines conditions for ending a chat round, such as explicit function calls (`end_planner_turn`) or text mentions (`TASK COMPLETE`, `TASK FAILED`).
*   **`agent_names.py`**:
    *   Defines string constants for the names of all agents (`HUBSPOT_AGENT_NAME`, `SY_API_AGENT_NAME`, `PLANNER_AGENT_NAME`, `PRODUCT_AGENT_NAME`, `USER_PROXY_AGENT_NAME`). This helps avoid typos and circular dependencies.
*   **Planner Agent (`src/agents/planner/`)**: The central orchestrator.
    *   `planner_agent.py`: Contains `create_planner_agent` to instantiate the Planner `AssistantAgent`.
    *   `system_message.py` (`PLANNER_ASSISTANT_SYSTEM_MESSAGE`): Provides a highly detailed system prompt for the Planner Agent. This prompt outlines:
        *   **Role & Goal**: Coordinator for StickerYou, stateless backend operation, single response cycle.
        *   **Interaction Modes**: Customer Service and Developer Interaction (triggered by `-dev`).
        *   **Core Capabilities & Limitations**: Cannot execute tools directly (except `end_planner_turn`), must delegate. Defines scope (product range, no payments).
        *   **Specialized Agents**: Describes the Product, SY API, and HubSpot agents and when to delegate to them.
        *   **Workflow Strategy**: Detailed workflows for various scenarios, including:
            *   General approach (internal thinking -> single response).
            *   Developer interaction.
            *   Handling dissatisfaction and handoffs (multi-turn).
            *   Standard failure handoffs (tool failure, product not found).
            *   Handling silent agent responses (with retries).
            *   Product identification and information gathering.
            *   **Price Quoting**: A critical multi-step workflow involving getting a Product ID from the Product Agent *first*, then size/quantity, then price from the SY API Agent. Emphasizes not assuming Product IDs.
            *   Order status and tracking requests.
        *   **Output Formats**: Strict formats for delegation messages, final user responses (questions, success, failure), and developer mode answers.
        *   **Critical Rules**: Emphasizes ending the turn correctly with `end_planner_turn`, no internal monologue in user-facing replies, data integrity (no hallucination, mandatory Product ID verification from Product Agent).
*   **Product Agent (`src/agents/product/`)**: Expert on product information.
    *   `product_agent.py`:
        *   `create_product_agent`: Instantiates the Product `AssistantAgent`.
        *   **Product List Preloading**: Attempts to fetch the entire product list using `sy_list_products` on initialization and load it into the agent's memory in chunks. This is an optimization to reduce live API calls.
    *   `system_message.py` (`PRODUCT_ASSISTANT_SYSTEM_MESSAGE`): Defines the Product Agent's behavior:
        *   **Role & Goal**: Interpret product data (from preloaded memory or live API via `sy_list_products` tool) to find Product IDs, list/filter products, count products, and summarize details.
        *   **Memory Prioritization**: Instructed to check memory for preloaded product chunks first, combine them, and only use the `sy_list_products` tool if memory is unavailable or processing fails.
        *   **Capabilities**: Search/filter product list, identify best matching Product ID.
        *   **Limitations**: **No pricing capabilities.** Interacts only with Planner.
        *   **Output Formats**: Specific formats for returning a single Product ID (`Product ID found: [ID]`), multiple matches, filtered lists, counts, or errors.
*   **StickerYou API Agent (`src/agents/stickeryou/`)**: Interacts with the StickerYou API.
    *   `sy_api_agent.py`: Contains `create_sy_api_agent` to instantiate the SY API `AssistantAgent`.
    *   `system_message.py` (`SY_API_AGENT_SYSTEM_MESSAGE`): Governs the SY API Agent:
        *   **Role & Goal**: Execute functions for allowed SY API endpoints (orders, pricing, user auth checks). **Does not handle product listing.**
        *   **Tool Scopes**: Defines usage scopes for its tools (`[User, Dev, Internal]`, `[Dev Only]`, `[Internal Only]`).
        *   **Tools Available**: Lists tools like `sy_get_specific_price`, `sy_get_price_tiers`, `sy_get_order_details`, `sy_get_order_tracking`, `sy_cancel_order`, etc. (all functions from `src.tools.sticker_api.sy_api`).
        *   **Workflow**: Receive delegation -> Validate parameters -> Call tool -> Validate tool response -> Return exact result (Pydantic model/dict/list or error string).
        *   **Output Formats**: Raw JSON/list for success, or specific error strings (`SY_TOOL_FAILED:...`, `Error: Missing mandatory parameter(s)...`).
        *   **Critical Rule**: Must not return empty messages or `None`; defaults to an internal failure error if no valid data or specific error.
*   **HubSpot Agent (`src/agents/hubspot/`)**: Interacts with the HubSpot Conversations API.
    *   `hubspot_agent.py`: Contains `create_hubspot_agent` to instantiate the HubSpot `AssistantAgent`.
    *   `system_message.py` (`hubspot_agent_system_message`): Details the HubSpot Agent's role:
        *   **Role & Goal**: Interact with HubSpot Conversations API for threads, messages, actors, channels, inboxes, as instructed by Planner.
        *   **Tool Scopes**: Defines usage scopes (`[Dev, Internal]`, `[Dev Only]`).
        *   **Tools Available**: Lists tools like `send_message_to_thread`, `get_thread_details`, `get_thread_messages`, `list_threads`, `archive_thread`, etc. (all functions from `src.tools.hubspot.conversation_tools`).
        *   **Workflow**: Receive delegation -> Identify tool -> Validate parameters -> Call tool -> Return exact result (JSON dict/list or error string).
        *   **Output Formats**: Raw JSON/dict/list for success, or specific error strings (`HUBSPOT_TOOL_FAILED:...`, `Error: Missing mandatory parameter(s)...`).

### 4. Tools (`src/tools/`)

This directory contains the functions that agents can call to interact with external services or perform specific actions.

*   **Planner Tools (`src/tools/planner/`)**:
    *   `planner_tools.py`:
        *   `end_planner_turn()`: A simple function called by the Planner Agent to explicitly signal the end of its processing turn. Its execution triggers a `FunctionCallTermination` condition in the `SelectorGroupChat`.
*   **StickerYou API Tools (`src/tools/sticker_api/`)**:
    *   `sy_api.py`: This is a crucial file containing all functions (tools) for interacting with the StickerYou API.
        *   `_make_sy_api_request()`: An internal helper function that handles the actual HTTP requests to the SY API using `httpx`. It manages:
            *   Adding the Authorization header with the dynamic API token from `config`.
            *   Automatic token refresh on 401 Unauthorized errors (retries once).
            *   JSON request/response handling.
            *   Error handling for various HTTP status codes and network issues, returning standardized error strings prefixed with `API_ERROR_PREFIX`.
        *   **Tool Functions**: Each function maps to a StickerYou API endpoint, such as:
            *   Designs: `sy_create_design`, `sy_get_design_preview`.
            *   Orders: `sy_list_orders_by_status_get`, `sy_list_orders_by_status_post`, `sy_create_order`, `sy_create_order_from_designs`, `sy_get_order_details`, `sy_cancel_order`, `sy_get_order_item_statuses`, `sy_get_order_tracking`.
            *   Pricing & Products: `sy_list_products` (used by Product Agent for preloading), `sy_get_price_tiers`, `sy_get_specific_price`, `sy_list_countries`.
            *   Users: `sy_verify_login`, `sy_perform_login` (used for token refresh).
        *   Each tool function uses `_make_sy_api_request` and is typed to return either a Pydantic model representing the successful JSON response or an error string.
    *   **Data Transfer Objects (`src/tools/sticker_api/dtos/`)**: Pydantic models are used extensively for validating and structuring data for API requests and responses.
        *   `common.py`: Defines shared Pydantic models and enums like `OrderStatusId`, `AccessoryOption`, `ShipToAddress`, `OrderItemBase`.
        *   `requests.py`: Defines Pydantic models for SY API **request** bodies (e.g., `LoginRequest`, `SpecificPriceRequest`, `CreateOrderRequest`).
        *   `responses.py`: Defines Pydantic models for SY API **response** bodies (e.g., `LoginResponse`, `CountriesResponse`, `SpecificPriceResponse`, `PriceTiersResponse`, `ProductListResponse`, `OrderDetailResponse`). RootModels are used for responses that are lists of objects.
*   **HubSpot Tools (`src/tools/hubspot/`)**:
    *   `conversation_tools.py`: Contains all functions (tools) for interacting with the HubSpot Conversations API.
        *   `_make_hubspot_api_request()`: An internal helper function using the initialized `HUBSPOT_CLIENT` from `config` to make API requests. It handles different HTTP methods, query parameters, JSON payloads, and error conditions, returning a parsed JSON response or an error string prefixed with `ERROR_PREFIX`.
        *   **Tool Functions**: Each function maps to a HubSpot Conversations API endpoint:
            *   Actors: `get_actor_details`, `get_actors_batch`.
            *   Channels & Accounts: `get_channel_account_details`, `get_channel_details`, `list_channel_accounts`, `list_channels`.
            *   Inboxes: `get_inbox_details`, `list_inboxes`.
            *   Messages: `get_message_details`, `get_original_message_content`, `send_message_to_thread` (this one has logic to determine if it's a `MESSAGE` or `COMMENT` based on content and uses `clean_agent_output`).
            *   Threads: `archive_thread`, `get_thread_details`, `get_thread_messages`, `list_threads`, `update_thread`.
        *   Each tool function is typed to return either a Pydantic model representing the successful JSON response or an error string.
    *   `dto_requests.py`: Pydantic models for HubSpot Conversations API **request** bodies (e.g., `BatchReadActorsRequest`, `CreateMessageRequest`, `UpdateThreadRequest`).
    *   `dto_responses.py`: Pydantic models for HubSpot Conversations API **response** bodies (e.g., `ThreadDetail`, `ListMessagesResponse`, `ActorDetailResponse`, `MessageDetail`). Enums like `MessageType`, `ThreadStatus` are also defined here.

### 5. Services (`src/services/`)

Utility functions and services that support the main application logic but are not agents or direct tools.

*   **`hubspot_webhook_handler.py`**:
    *   Manages the processing of incoming HubSpot webhook notifications, specifically for new messages.
    *   `process_incoming_hubspot_message()`: A background task that:
        *   Fetches full message details using `get_message_details` tool.
        *   Checks if the message is relevant (incoming, from a visitor, type `MESSAGE`).
        *   If relevant, triggers the `agent_service.run_chat_session()` to get a response.
        *   Calls `process_agent_response()` to send the agent's reply back to the HubSpot thread using `send_message_to_thread`.
    *   **Deduplication**: Uses `PROCESSING_MESSAGE_IDS` set and an `asyncio.Lock` (`is_message_being_processed`, `add_message_to_processing`, `remove_message_from_processing`) to prevent processing the same message multiple times if HubSpot sends duplicate webhooks.
    *   `process_agent_response()`: Extracts the final reply from the `TaskResult` (looking for the Planner's message before the `end_planner_turn` call) and sends it to HubSpot.
*   **`sy_refresh_token.py`**:
    *   `refresh_sy_token()`: An asynchronous function that attempts to fetch a new StickerYou API token using credentials from `config` by calling `sy_perform_login`.
    *   Updates the token in the `config` module using `set_sy_api_token`.
    *   This service is called at server startup and by the `_make_sy_api_request` helper upon encountering a 401 error.
*   **`clean_agent_tags.py`**:
    *   `clean_agent_output()`: A utility function to remove internal tags (like `TASK COMPLETE:`, `TASK FAILED:`, `<UserProxyAgent>`, `<user_proxy>`) from the Planner Agent's final response before it's sent to the user or external systems.

### 6. Models (`src/models/`)

Pydantic models used for API endpoint request/response validation and data structuring, distinct from the DTOs used for external API interactions.

*   **`chat_api.py`**:
    *   `ChatRequest`: Defines the request body for the `/chat` endpoint (expects `message` and optional `conversation_id`).
    *   `ChatResponse`: Defines the response body for the `/chat` endpoint (includes `reply`, `conversation_id`, `stop_reason`, and optional `error`).
*   **`hubspot_webhooks.py`**:
    *   `HubSpotSubscriptionType` (Enum): Defines known HubSpot webhook subscription types (`conversation.creation`, `conversation.newMessage`).
    *   `HubSpotNotification`: Pydantic model representing a single notification event within a HubSpot webhook payload.
    *   `WebhookPayload`: Type alias for `List[HubSpotNotification]`, representing the overall structure of the webhook data received from HubSpot.

### 7. Supporting Files

*   **`.env-example`**: A template file showing the required environment variables for configuring the application (API keys, base URLs, default IDs, LLM settings).
*   **`.gitignore`**: Standard Python gitignore file, listing files and directories to be excluded from version control (e.g., `__pycache__`, `.env`, `venv/`).
*   **`.pylintrc`**: Configuration file for Pylint, specifying disabled checks (e.g., line length) and formatting options.
*   **`agent-chatbot.code-workspace`**: VS Code workspace configuration file, defining folders and settings (like format on save).
*   **`README.md`**: Provides an overview of the project, setup, and execution instructions.
*   **`possible_messages.md`**: Contains a comprehensive list of example user messages designed to test various scenarios and agent workflows, including success cases, failure/handoff scenarios, and developer mode interactions for each agent and API.
*   **`system_message_template.md`**: A generic template for creating system messages for new agents, outlining the typical sections (Role & Goal, Capabilities, Tools, Workflow, Output Format, Rules, Examples).
