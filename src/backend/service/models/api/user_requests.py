"""
Defines data models used for user requests in the API
"""

from typing import Optional

from pydantic import EmailStr, Field

from ..custom_base_model import CustomBaseModel


class APIUserRequest(CustomBaseModel):
    """A user request as represented in the API"""

    email: EmailStr
    company: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    role_requested: str


class APIActionUserRequest(CustomBaseModel):
    """A user request as represented in the API"""

    email: EmailStr
    action: str


class APIGetUserRequestsResponse(CustomBaseModel):
    """A list of user requests as represented in the get user requests API"""

    requests: list[APIUserRequest]
    last_key: Optional[str] = None
