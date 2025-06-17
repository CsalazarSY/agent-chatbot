import config
from src.tools.hubspot.conversation.conversation_tools import (
    get_thread_details,
    send_message_to_thread,
)
from src.tools.hubspot.conversation.dto_requests import CreateMessageRequest
from src.markdown_info.ACK_message import ACK_MESSAGE_HTML, ACK_MESSAGE_TEXT


async def send_ack_of_received_to_conversation(conversation_id: str):
    """
    Sends an acknowledgment message to a HubSpot conversation to indicate
    that the bot is processing the request.
    """
    try:
        # 1. Construct the message payload using the CreateMessageRequest DTO
        message_payload = CreateMessageRequest(
            type="MESSAGE",
            text=ACK_MESSAGE_TEXT,
            richText=ACK_MESSAGE_HTML,
            senderActorId=config.HUBSPOT_DEFAULT_SENDER_ACTOR_ID,
            channelId=config.HUBSPOT_DEFAULT_CHANNEL,
            channelAccountId=config.HUBSPOT_DEFAULT_CHANNEL_ACCOUNT,
        )

        # 2. Use the conversation tool to send the message
        result = await send_message_to_thread(
            thread_id=conversation_id, message_request_payload=message_payload
        )

        if isinstance(result, str):
            # If the tool returns a string, it's an error message
            print(
                f"Failed to send acknowledgment message to conversation {conversation_id}: {result}"
            )
            return

    except Exception as e:
        print(
            f"An unexpected error occurred while sending acknowledgment for conversation {conversation_id}: {e}"
        )
