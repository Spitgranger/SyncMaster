"""
Defines structure of a site visit in the API
"""

from datetime import datetime
from typing import Optional

from pydantic import Field, model_validator
from typing_extensions import Self

from ..custom_base_model import CustomBaseModel
from .file_attachment import APIFileAttachment


class APISiteVisit(CustomBaseModel):
    """A site visit as represented in the API"""

    site_id: str
    user_id: str
    entry_time: datetime
    allowed_tracking: bool
    ack_status: bool
    exit_time: Optional[datetime] = None
    work_order: Optional[int] = None
    description: Optional[str] = None
    on_site: Optional[bool] = None
    attachments: list[APIFileAttachment] = Field(default_factory=list)


class APIEnterSiteRequest(CustomBaseModel):
    """The body of a request to enter a site"""

    allowed_tracking: bool
    ack_status: bool
    on_site: Optional[bool] = None

    @model_validator(mode="after")
    def require_on_site_if_tracking_location(self) -> Self:
        """
        Validates that if location is being tracked, then we must
        know whether or not the user is on site
        """
        if self.allowed_tracking and self.on_site == None:
            raise ValueError("[allowed_tracking] = true, must provide [on_site]")
        return self


class EditableSiteVisitDetails(CustomBaseModel):
    """The details of a site visit which are editable"""

    work_order: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=200)


class APIListSiteVisitResponse(CustomBaseModel):
    """A list of site visit as represented in the get site visits API"""

    visits: list[APISiteVisit]
    last_key: Optional[str] = None
