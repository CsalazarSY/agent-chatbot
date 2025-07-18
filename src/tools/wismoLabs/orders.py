""" This module provides tools to interact with the WismoLabs API for order status retrieval. """
import httpx
import config
import json
from typing import Dict
from pydantic import ValidationError
from src.services.logger_config import log_message
from src.tools.wismoLabs.dtos.response import WismoAuthResponse, WismoOrderStatusResponse

# --- Constants ---
WISMO_V1_TOOL_ERROR_PREFIX = "WISMO_V1_TOOL_FAILED:"

# --- Authentication Helper ---
async def _authenticate_wismo() -> str:
    """
    Authenticates with WismoLabs API and returns a token.
    Returns error string if authentication fails.
    """
    if not all([config.WISMOLABS_API_URL, config.WISMOLABS_USERNAME, config.WISMOLABS_PASSWORD]):
        return f"{WISMO_V1_TOOL_ERROR_PREFIX} Configuration Error - Missing WismoLabs API credentials."
    
    auth_url = f"{config.WISMOLABS_API_URL}/auth"
    # Use the same headers as working Postman request
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    payload = {
        "username": config.WISMOLABS_USERNAME,
        "password": config.WISMOLABS_PASSWORD
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(auth_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                try:
                    auth_response = WismoAuthResponse.model_validate(response.json())
                    config.set_wismo_api_token(auth_response.token)
                    return auth_response.token
                except ValidationError as e:
                    log_message(f"WismoLabs auth response validation error: {e}", log_type="error")
                    return f"{WISMO_V1_TOOL_ERROR_PREFIX} Invalid authentication response format."
            else:
                error_detail = f"Status: {response.status_code}"
                try:
                    error_body = response.json()
                    error_detail += f", Body: {json.dumps(error_body)[:200]}"
                except json.JSONDecodeError:
                    error_detail += f", Body: {response.text[:200]}"
                
                log_message(f"WismoLabs authentication failed: {error_detail}", log_type="error")
                return f"{WISMO_V1_TOOL_ERROR_PREFIX} Authentication failed: {error_detail}"

    except httpx.TimeoutException:
        return f"{WISMO_V1_TOOL_ERROR_PREFIX} Authentication timed out."
    except httpx.RequestError as req_err:
        return f"{WISMO_V1_TOOL_ERROR_PREFIX} Network error during authentication: {req_err}"
    except Exception as e:
        log_message(f"Unexpected error during WismoLabs authentication: {e}", log_type="error")
        return f"{WISMO_V1_TOOL_ERROR_PREFIX} Unexpected authentication error: {e}"

# --- Public Tool Function ---
async def get_wismo_order_status(order_id: str) -> Dict | str:
    """
    Retrieves the status of a specific order by its order ID from the WismoLabs v1 API.
    
    Args:
        order_id: The order ID to search for.

    Returns:
        A dictionary with the detailed order status on success, or an error string on failure.
    """
    if not order_id:
        return f"{WISMO_V1_TOOL_ERROR_PREFIX} An Order ID must be provided."

    # First, ensure we have a valid token
    current_token = config.get_wismo_api_token()
    if not current_token:
        auth_result = await _authenticate_wismo()
        if auth_result.startswith(WISMO_V1_TOOL_ERROR_PREFIX):
            return auth_result
        current_token = auth_result

    # Make the order status request
    api_url = f"{config.WISMOLABS_API_URL}/order-status"
    headers = {
        "Cache-Control": "no-cache",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Authorization": f"Bearer {current_token}",
    }
    params = {"orderId": order_id}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers, params=params)

            if response.status_code == 200:
                try:
                    # Validate and serialize the successful response
                    order_status = WismoOrderStatusResponse.model_validate(response.json())
                    return order_status.model_dump(by_alias=True)
                except ValidationError as e:
                    log_message(f"WismoLabs response validation error for order {order_id}: {e}", log_type="error")
                    return f"{WISMO_V1_TOOL_ERROR_PREFIX} API response did not match expected format."
            
            elif response.status_code == 401:
                # Try to re-authenticate once
                auth_result = await _authenticate_wismo()
                if auth_result.startswith(WISMO_V1_TOOL_ERROR_PREFIX):
                    return auth_result
                
                # Retry the request with new token
                headers = {
                    "Cache-Control": "no-cache",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Authorization": f"Bearer {auth_result}",
                }
                response = await client.get(api_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    try:
                        order_status = WismoOrderStatusResponse.model_validate(response.json())
                        return order_status.model_dump(by_alias=True)
                    except ValidationError as e:
                        return f"{WISMO_V1_TOOL_ERROR_PREFIX} API response did not match expected format."
                else:
                    error_detail = f"Status: {response.status_code}"
                    try:
                        error_body = response.json()
                        error_detail += f", Body: {json.dumps(error_body)[:200]}"
                    except json.JSONDecodeError:
                        error_detail += f", Body: {response.text[:200]}"
                    return f"{WISMO_V1_TOOL_ERROR_PREFIX} Request failed after re-authentication: {error_detail}"
            
            else:
                error_detail = f"Status: {response.status_code}"
                try:
                    error_body = response.json()
                    error_detail += f", Body: {json.dumps(error_body)[:200]}"
                except json.JSONDecodeError:
                    error_detail += f", Body: {response.text[:200]}"
                
                if response.status_code == 404:
                    return f"{WISMO_V1_TOOL_ERROR_PREFIX} Order not found (404): {error_detail}"
                else:
                    return f"{WISMO_V1_TOOL_ERROR_PREFIX} Request failed: {error_detail}"

    except httpx.TimeoutException:
        return f"{WISMO_V1_TOOL_ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{WISMO_V1_TOOL_ERROR_PREFIX} Network/Connection Error: {req_err}"
    except Exception as e:
        return f"{WISMO_V1_TOOL_ERROR_PREFIX} Unexpected error: {e}"
