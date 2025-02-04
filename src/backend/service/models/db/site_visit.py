"""
Defines the model for a site visit as represented in the database
"""

from datetime import date, datetime, time
from typing import Optional

from pydantic import computed_field

from ...util import ItemType
from .db_base import DBItemModel


class DBSiteVisit(DBItemModel):
    user_id = str
    site_id = str
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

    @computed_field
    @property
    def gsi_1_pk(self) -> str:
        return self.item_type().value

    @computed_field
    @property
    def gsi_1_sk(self) -> str:
        return self.exit_time.isoformat()
