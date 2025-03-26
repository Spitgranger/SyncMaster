"""
A data model for a user request in the database
"""

from pydantic import EmailStr, computed_field

from ...util import ItemType
from ..api.user_requests import APIUserRequest
from .db_base import DBItemModel


class DBUserRequest(DBItemModel):
    """Model representing a user request in the database"""

    email: EmailStr
    company: str
    name: str
    role_requested: str

    @staticmethod
    def item_type() -> ItemType:
        return ItemType.USER_REQUEST

    @computed_field
    @property
    def pk(self) -> str:
        return f"{self.item_type().value}"

    @computed_field
    @property
    def sk(self) -> str:
        return self.email

    def to_api_model(self) -> APIUserRequest:
        """
        The user request as an API model, without the DB specific attributes

        :return: A representation of the site visits for the API
        """
        return APIUserRequest(
            email=self.email,
            company=self.company,
            role_requested=self.role_requested,
            name=self.name,
        )
