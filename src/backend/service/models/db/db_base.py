from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel, computed_field
from pydantic.config import ConfigDict

from datetime import datetime


class DBItemModel(BaseModel, ABC):
    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
        loc_by_alias=True,
        populate_by_name= True,
        use_enum_values=True,
    )

    last_modified_by: str
    last_modified_time: datetime

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs, exclude_none=True, by_alias=True, mode="json")

    def model_dump_json(self, *args, **kwargs):
        return super().model_dump_json(*args, **kwargs, exclude_none=True, by_alias=True)
    
    @staticmethod
    @property
    def item_type() -> str: 
        ...


    @abstractmethod
    @computed_field
    @property
    def pk(self) -> str:
        ...

    @abstractmethod
    @computed_field
    @property
    def sk(self) -> str:
        ...

    @computed_field
    @property
    def gsi_1_pk(self) -> str:
        return f"{self.item_type}#{self.last_modified_by}"
