"""
Defines structure of a site in the API
"""

from decimal import Decimal
from typing import Optional

from pydantic import Field

from ..custom_base_model import CustomBaseModel


class APISite(CustomBaseModel):
    """A site as represented in the API"""

    site_id: str = Field(..., min_length=5, max_length=5)
    longitude: Decimal
    latitude: Decimal
    acceptable_range: Decimal


class APISitePartial(CustomBaseModel):
    """A partial representation of a site, containing only attributes that can be updated"""

    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    acceptable_range: Optional[Decimal] = None


class APIListSitesResponse(CustomBaseModel):
    """A list of sitesas represented in the list sites API"""

    sites: list[APISite]
    last_key: Optional[str] = None
