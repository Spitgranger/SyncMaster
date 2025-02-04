"""
Defines the abstract base model for all database items to implement
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, computed_field
from pydantic.config import ConfigDict

from ...util import ItemType


class DBItemModel(BaseModel, ABC):
    """
    An abstract model representing a database item that all database items must implement
    """

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
        loc_by_alias=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    last_modified_by: str
    last_modified_time: datetime

    def model_dump(self, *args, **kwargs) -> dict:
        return super().model_dump(*args, **kwargs, exclude_none=True, by_alias=True, mode="json")

    def model_dump_json(self, *args, **kwargs) -> str:
        return super().model_dump_json(*args, **kwargs, exclude_none=True, by_alias=True)

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
    def gsi_1_pk(self) -> str:
        """The hash key for GSI 1, formatted as `{item_type}#{last_modified_by}`"""
        return f"{self.item_type()}#{self.last_modified_by}"

    @computed_field
    @property
    def gsi_1_sk(self) -> str:
        """The range key for GSI 1, formatted as `{last_modified_date}`"""
        return self.last_modified_time.isoformat()
