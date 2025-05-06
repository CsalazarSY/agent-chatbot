# Agent Chatbot

This project implements a multi-agent chatbot system using AutoGen. The goal is to create a conversational AI capable of handling specific user requests related to product pricing and HubSpot interactions.

## System Architecture

The system consists of several specialized agents coordinated by a central Planner Agent:

- **Planner Agent:** Orchestrates the conversation flow, analyzes user intent, delegates tasks to specialized agents, and communicates results back to the user.
- **Product Agent:** Identifies product IDs based on user descriptions using a predefined data source or live API calls. It can also list, filter, and count products.
- **StickerYou API Agent (SY API Agent):** Interacts with the StickerYou API for tasks like fetching price quotes (specific and tiered), managing orders (details, tracking, cancellation), and listing supported countries. It does not handle product listing/interpretation.
- **HubSpot Agent:** Interacts with the HubSpot Conversations API to manage threads, send messages/comments, and retrieve information about actors, channels, and inboxes.
- **User Proxy Agent:** Represents the user within the AutoGen framework.

The agents interact through a FastAPI backend server, which provides API endpoints (`/chat` and `/hubspot/webhooks`) for external interactions.

## Getting Started

Follow these steps to set up and run the Agent Chatbot project locally.

### Prerequisites

*   Python 3.10 or later.
*   Conda (recommended for managing environments) or `venv`.

### Environment Setup

It's highly recommended to use a virtual environment.

**Using Conda:**

1.  Install Conda if you haven't already.
2.  Create and activate a new Conda environment:
    ```bash
    conda create -n autogen python=3.12
    conda activate autogen
    ```
3.  To deactivate the environment later:
    ```bash
    conda deactivate
    ```

**Using `venv`:**

1.  Navigate to the project root directory.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
4.  To deactivate later:
    ```bash
    deactivate
    ```

### Installation

1.  **Install dependencies:**
    The primary way to install dependencies is using the `environment.yml` file with Conda:
    ```bash
    conda env update --file environment.yml --prune
    ```
    This will install all necessary packages including:
    *   `autogen-agentchat==0.5.5`
    *   `autogen-core==0.5.5`
    *   `autogen-ext==0.5.5` (includes OpenAI, Azure, and MCP extensions)
    *   `fastapi`
    *   `uvicorn`
    *   `httpx`
    *   `hubspot-api-client==11.1.0`
    *   `pydantic==2.11.3` (and related `pydantic-core`, `pydantic-settings`)
    *   `python-dotenv==1.1.0`
    *   `black` (for code formatting)

    If you prefer using `pip` directly after setting up a Python 3.12 environment:
    ```bash
    pip install -U autogen-agentchat autogen-core autogen-ext[azure,mcp,openai] fastapi uvicorn httpx hubspot-api-client pydantic python-dotenv black
    ```

### Configuration

1.  Copy the `.env-example` file to a new file named `.env` in the project root:
    ```bash
    cp .env-example .env
    ```
2.  Open the `.env` file and fill in the required API keys, base URLs, and other configuration values as described in the comments within the file. This includes:
    *   StickerYou API credentials (`SY_API_USERNAME`, `SY_API_PASSWORD`, `API_BASE_URL`).
    *   HubSpot API token and default IDs (`HUBSPOT_API_TOKEN`, etc.).
    *   LLM provider details (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL_NAME`).

## Running the Application

1.  **Start the FastAPI Server:**
    Open a terminal, ensure your virtual environment is activated, and run:
    ```bash
    python main_server.py
    ```
    The server will typically start on `http://0.0.0.0:8000`. `uvicorn` will provide live reloading for development.

2.  **Expose for HubSpot Webhooks (if needed):**
    To receive HubSpot webhooks on your local machine, you'll need to expose your local server to the internet. `localtunnel` is one way to achieve this:
    Open another terminal and run:
    ```bash
    npx localtunnel --subdomain api-hubsbot --port 8000
    ```
    Replace `api-hubsbot` with your desired subdomain. This will give you a public URL (e.g., `https://api-hubsbot.loca.lt`) that you can configure as your HubSpot webhook URL.

3.  **Testing with CLI (Optional):**
    To interact with the agent system via the command line for testing:
    ```bash
    python main.py
    ```

## Project Structure

The project is organized into several key directories:
*   `src/agents/`: Contains the definitions for all AutoGen agents (Planner, Product, SY API, HubSpot) including their creation logic and system messages.
    *   `agents_services.py`: Manages agent creation, shared state, and chat session execution.
*   `src/tools/`: Defines the tools (functions) that agents can call to interact with external APIs (StickerYou, HubSpot) or perform specific actions.
    *   Includes Data Transfer Object (DTO) Pydantic models for API request/response validation.
*   `src/services/`: Contains utility services like HubSpot webhook handling, SY API token refreshing, and cleaning agent output tags.
*   `src/models/`: Pydantic models for the FastAPI `/chat` endpoint and HubSpot webhook payloads.
*   `config.py`: Handles loading and validation of environment variables and API client initialization.
*   `main_server.py`: FastAPI application entry point.
*   `main.py`: CLI application entry point.

For a more detailed breakdown of the codebase, please refer to: 

## Usage

- See `possible_messages.md` for example user messages and expected system behavior across various scenarios.
- Refer to `system_message_template.md` for the standard template used to define agent system messages.
- For a comprehensive understanding of the codebase, review the detailed **Codebase Summary** document.
