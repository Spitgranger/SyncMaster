"""
Defines the abstract base model for all database items to implement
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import computed_field

from ...util import ItemType
from ..custom_base_model import CustomBaseModel


class DBItemModel(CustomBaseModel, ABC):
    """
    An abstract model representing a database item that all database items must implement
    """

    last_modified_by: str
    last_modified_time: datetime

    @staticmethod
    @abstractmethod
    def item_type() -> ItemType:
        """The type of the database item"""

    @computed_field
    @property
    @abstractmethod
    def pk(self) -> str:
        """The partition key of the database item, this is the hash key for the database"""

    @computed_field
    @property
    @abstractmethod
    def sk(self) -> str:
        """The sort key of the database item, this is the range key for the database"""

    @computed_field
    @property
    def type(self) -> ItemType:
        """A computed field containing the schemas item type"""
        return self.item_type()
