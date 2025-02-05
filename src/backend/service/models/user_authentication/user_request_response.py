from typing import Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    name: str
    password: str = Field(..., min_length=8)
    attributes: Dict[str, str] = Field(default_factory=dict)


class AdminSignupRequest(BaseModel):
    email: EmailStr
    name: str
    attributes: Dict[str, str] = Field(default_factory=dict)


class SigninRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    new_password: Optional[str] = Field(default=None)
