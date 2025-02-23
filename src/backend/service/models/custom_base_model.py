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

    def model_dump(self, *args, **kwargs) -> dict:
        kwargs["exclude_none"] = kwargs.get("exclude_none", True)
        kwargs["by_alias"] = kwargs.get("by_alias", True)
        kwargs["mode"] = kwargs.get("mode", "json")
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs) -> str:
        kwargs["exclude_none"] = kwargs.get("exclude_none", True)
        kwargs["by_alias"] = kwargs.get("by_alias", True)
        return super().model_dump_json(*args, **kwargs)
