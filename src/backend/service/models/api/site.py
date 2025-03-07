from typing import Optional

from pydantic import field_validator

from ..custom_base_model import CustomBaseModel


class APISite(CustomBaseModel):
    site_id: str
    longitude: float
    latitude: float
    acceptable_range: float

    @field_validator("site_id")
    def validate_site_id(cls, value):
        if value == "ALL":
            raise ValueError("Site ID cannot be 'ALL'")
        return value


class APISitePartial(CustomBaseModel):
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    acceptable_range: Optional[float] = None


class APIListSitesResponse(CustomBaseModel):
    sites: list[APISite]
    last_key: Optional[str] = None
