from typing import Dict, Optional, List

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    attributes: Dict[str, str] = Field(default_factory=dict)


class AdminSignupRequest(BaseModel):
    email: EmailStr
    attributes: Dict[str, str] = Field(default_factory=dict)


class SigninRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    new_password: Optional[str] = Field(default=None)


class UpdateUserAttributeRequest(BaseModel):
    email: EmailStr
    attributes: List[Dict[str, str]]


class GetUsersByAttributeRequest(BaseModel):
    attributes: Dict[str, str] = Field(default_factory=dict)
