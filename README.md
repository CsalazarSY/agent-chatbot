# Agent Chatbot

This project implements a multi-agent chatbot system using the `autogen` framework designed for customer service interactions, particularly for a company like StickerYou.

## Core Functionality

The system uses a `Planner Agent` to orchestrate conversations. Based on user requests, the Planner delegates tasks to specialized agents:

*   **`Product Agent`**: Answers product-related questions by **querying a ChromaDB vector store** containing website information. Uses a specific tool (`sy_list_products`) only when explicitly asked by the Planner to find a Product ID or list products.
*   **`Price Quote Agent`**: Interacts with the StickerYou API for tasks like price calculation (specific prices, tier pricing) and listing supported countries. It no longer handles order status or tracking.
*   **`HubSpot Agent`**: Manages interactions with the HubSpot Conversations API, primarily used by the Planner to **create support tickets** during handoffs after collecting the user's email address.

The Planner manages the flow, ensuring correct information is gathered (like Product IDs before pricing), handles errors, informs users about features currently in development (such as order status/tracking) by offering to create support tickets, and facilitates handoffs to human agents by creating HubSpot tickets when necessary.

## Features

*   Multi-agent architecture using `autogen`.
*   Specialized agents for distinct tasks (Product Info, Price Quotes, HubSpot).
*   RAG implementation using **ChromaDB** for the Product Agent.
*   Detailed workflow management by the Planner Agent.
*   Error handling and automated handoff via **HubSpot ticket creation**.
*   Integration with HubSpot Webhooks for real-time chat interaction.
*   Developer mode (`-dev`) for debugging and direct interaction.

## Setup

1.  Clone the repository.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the environment: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows).
4.  Install dependencies: `pip install -r requirements.txt` (or use `conda env update --file environment.yml --prune` if using Conda with the provided file)
5.  Configure environment variables (e.g., in a `.env` file): Set API keys for OpenAI, StickerYou, HubSpot, and configure ChromaDB path/settings.
6.  Run the main application script (e.g., `python src/main.py` or `python main_server.py` for the server).

## Key Components

*   **Agents (`src/agents/`)**: Definitions and system messages for each agent.
*   **Tools (`src/tools/`)**: Functions callable by the agents (SY API wrappers for pricing; HubSpot tools). Note: Order management tools exist in `sy_api.py` but are not used by the `PriceQuoteAgent`.
*   **Configuration (`config.py`, `.env`)**: API keys and settings.
*   **Main Application (`src/main.py` or `main_server.py`)**: Server setup (e.g., FastAPI), webhook handling, agent initialization, chat management.

## System Architecture

The system consists of several specialized agents coordinated by a central Planner Agent:

- **Planner Agent:** Orchestrates the conversation flow, analyzes user intent, delegates tasks to specialized agents, informs users if a requested feature (e.g., order tracking) is in development and offers support tickets, and communicates results back to the user.
- **Product Agent:** Identifies product IDs based on user descriptions using a predefined data source or live API calls. It can also list, filter, and count products.
- **Price Quote Agent (formerly SY API Agent):** Interacts with the StickerYou API for tasks like fetching price quotes (specific and tiered) and listing supported countries. It does not handle product listing/interpretation or order management.
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
2.  Create and activate a new Conda environment from the `environment.yml` file:
    ```bash
    conda env create -f environment.yml
    conda activate autogen-chatbot # Or the name specified in environment.yml
    ```
    If you prefer to create it manually first:
    ```bash
    conda create -n autogen-chatbot python=3.12 # Ensure this matches your project's Python version
    conda activate autogen-chatbot
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
    If using Conda and you created the environment with `environment.yml`, dependencies are already installed.
    If you created the Conda environment manually or are using `venv`, install dependencies using the `environment.yml` for consistency (pip can also be used if you manage a requirements.txt):
    ```bash
    conda env update --file environment.yml --prune # If in an existing Conda env
    # or pip install -r requirements.txt (if you generate one)
    ```
    Key packages include:
    *   `autogen-agentchat`
    *   `autogen-core`
    *   `autogen-ext` (includes OpenAI, Azure, and MCP extensions)
    *   `fastapi`
    *   `uvicorn`
    *   `httpx`
    *   `hubspot-api-client`
    *   `pydantic`
    *   `python-dotenv`
    *   `black` (for code formatting)

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
    uvicorn main_server:app --reload
    ```
    The application will typically be available at `http://127.0.0.1:8000`.

2.  **Run the CLI (for testing):**
    Open another terminal, ensure your virtual environment is activated, and run:
    ```bash
    python main.py
    ```

## Project Structure Overview


## Delete __pycache__ folders
```bash
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
```

## Docker commands
```bash
docker build -t autogen-chatbot
```

```bash
docker run --rm -p 8000:8000 autogen-chatbot
```

### Build Image for Azure CR
```bash
docker build -f Dockerfile.base -t syqaaichatbotregistry.azurecr.io/autogen-chatbot-base:1.1 .
```

### Push the built image

```bash
docker push syqaaichatbotregistry.azurecr.io/autogen-chatbot-base:1.1
```

Remember to change the version of the image in both the docker image and update version in the dockerfile (not the base)
