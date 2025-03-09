from typing import Optional

from pydantic import Field

from ..custom_base_model import CustomBaseModel


class APISite(CustomBaseModel):
    site_id: str = Field(..., min_length=5, max_length=5)
    longitude: float
    latitude: float
    acceptable_range: float


class APISitePartial(CustomBaseModel):
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    acceptable_range: Optional[float] = None


class APIListSitesResponse(CustomBaseModel):
    sites: list[APISite]
    last_key: Optional[str] = None
