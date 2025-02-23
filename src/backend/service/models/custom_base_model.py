"""
Defines a customized model configuration for this project
"""

from pydantic import BaseModel
from pydantic.config import ConfigDict


class CustomBaseModel(BaseModel):
    """
    An customized base model, with a more relevant configuration
    """

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
        loc_by_alias=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    def model_dump(self, *args, exclude_none=True, by_alias=True, mode="json", **kwargs) -> dict:
        kwargs["exclude_none"] = exclude_none
        kwargs["by_alias"] = by_alias
        kwargs["mode"] = mode
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, exclude_none=True, by_alias=True, **kwargs) -> str:
        kwargs["exclude_none"] = exclude_none
        kwargs["by_alias"] = by_alias
        return super().model_dump_json(*args, **kwargs)
