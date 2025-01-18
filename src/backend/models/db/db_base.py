from __future__ import annotations

from abc import ABC, abstractmethod
from typing import NotRequired, Optional, TypedDict

from pydantic import BaseModel
from pydantic.alias_generators import to_pascal, to_snake
from pydantic.config import ConfigDict


class KeySchema(TypedDict):
    primary_key: str
    secondary_key: NotRequired[str]


class DatabaseBaseModel(BaseModel, ABC):
    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
        loc_by_alias=True,
        use_enum_values=True,
        alias_generator=to_pascal,
    )

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs, exclude_none=True, by_alias=True, mode="json")

    def model_dump_json(self, *args, **kwargs):
        return super().model_dump_json(*args, **kwargs, exclude_none=True, by_alias=True)

    @abstractmethod
    @staticmethod
    def key_schema(gsi: Optional[str] = None) -> KeySchema: ...

    @classmethod
    def create_key(cls, gsi: Optional[str] = None, **kwargs) -> dict:
        key_schema = cls.key_schema(gsi=gsi)
        key = {key_schema["primary_key"]: kwargs[to_snake(key_schema["primary_key"])]}
        if secondary_key_name := key_schema.get("secondary_key"):
            key[secondary_key_name] = kwargs[to_snake(secondary_key_name)]
        return key
