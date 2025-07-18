""" This module contains the request DTOs for the WismoLabs API. """
from pydantic import BaseModel

class WismoAuthRequest(BaseModel):
    """
    Represents the request body for authenticating with the WismoLabs API.
    """
    username: str
    password: str
