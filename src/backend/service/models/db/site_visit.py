"""
Defines the model for a site visit as represented in the database
"""

from datetime import datetime
from typing import Optional

from pydantic import Field, computed_field

from ...util import ItemType
from ..api.site_visit import APISiteVisit
from .db_base import DBItemModel


class DBSiteVisit(DBItemModel):
    """Model representing a site visit in the database"""

    user_id: str
    site_id: str
    entry_time: datetime
    loc_tracking: bool
    ack_status: bool
    exit_time: Optional[datetime] = None
    work_order: Optional[int] = None
    description: Optional[str] = None
    on_site: Optional[bool] = None
    attachments: dict[str, str] = Field(default_factory=dict)

    @staticmethod
    def item_type() -> ItemType:
        return ItemType.SITE_VISIT

    @computed_field
    @property
    def pk(self) -> str:
        return f"{self.item_type().value}#{self.site_id}#{self.user_id}"

    @computed_field
    @property
    def sk(self) -> str:
        return self.entry_time.isoformat()

    def to_api_model(self) -> APISiteVisit:
        """The site visit as an API model, without the DB specific attributes"""
        return APISiteVisit(
            site_id=self.site_id,
            user_id=self.user_id,
            entry_time=self.entry_time,
            allowed_tracking=self.loc_tracking,
            ack_status=self.ack_status,
            exit_time=self.exit_time,
            work_order=self.work_order,
            description=self.description,
            on_site=self.on_site,
        )
