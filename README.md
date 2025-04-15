# Agent Chatbot

This project implements a multi-agent chatbot system using AutoGen. The goal is to create a conversational AI capable of handling specific user requests related to product pricing and HubSpot interactions.

## System Architecture

The system consists of several specialized agents coordinated by a central Planner Agent:

- **Planner Agent:** Orchestrates the conversation flow, analyzes user intent, delegates tasks to specialized agents, and communicates results back to the user.
- **Product Agent:** Identifies product IDs based on user descriptions using a predefined data source.
- **Price Agent:** Fetches product price quotes using an external API, requiring product ID, dimensions, and quantity.
- **HubSpot Agent:** Sends messages or internal comments to specified HubSpot conversation threads.
- **User Proxy Agent:** Represents the user within the AutoGen framework.

The agents interact through a FastAPI backend server, which provides an API endpoint for a frontend UI.

## Usage

- See `possible_messages.md` for example user messages and expected system behavior.
- Refer to `system_message_template.md` for the standard template used to define agent system messages.
