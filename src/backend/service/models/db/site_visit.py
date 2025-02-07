"""
Defines the model for a site visit as represented in the database
"""

from datetime import datetime
from typing import Optional

from pydantic import computed_field

from ...util import ItemType
from ..api.site_visit import APISiteVisit
from .db_base import DBItemModel


class DBSiteVisit(DBItemModel):
    """Model representing a site visit in the database"""

    user_id: str
    site_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None

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
            exit_time=self.exit_time,
        )
