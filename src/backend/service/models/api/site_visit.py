"""
Defines structure of a site visit in the API
"""

from datetime import datetime
from typing import Optional

from ..custom_base_model import CustomBaseModel
from ..db.site_visit import DBFileAttachment

from pydantic import Field


class APIFileAttachment(CustomBaseModel):
    name: str
    url: str


class APISiteVisit(CustomBaseModel):
    """A site visit as represented in the API"""

    site_id: str
    user_id: str
    entry_time: datetime
    allowed_tracking: bool
    ack_status: bool
    exit_time: Optional[datetime] = None
    work_order: Optional[str] = None
    description: Optional[str] = None
    on_site: Optional[bool] = None
    attachments: list[APIFileAttachment] = Field(default_factory=list)


class APIEnterSiteRequest(CustomBaseModel):
    """The body of a request to enter a site"""

    allowed_tracking: bool
    ack_status: bool
    work_order: Optional[str] = None
    description: Optional[str] = None
    on_site: Optional[bool] = None


class EditableSiteVisitDetails(CustomBaseModel):
    """The details of a site visit which are editable"""

    work_order: Optional[str] = None
    description: Optional[str] = None
    on_site: Optional[bool] = None
    attachments: list[DBFileAttachment] = Field(default_factory=list)


class APIListSiteVisitResponse(CustomBaseModel):
    """A list of site visit as represented in the get site visits API"""

    visits: list[APISiteVisit]
    last_key: Optional[str] = None
