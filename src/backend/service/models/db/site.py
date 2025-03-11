"""
Defines structure of a site in the DB
"""

from decimal import Decimal

from pydantic import computed_field

from ...util import ItemType
from ..api.site import APISite
from .db_base import DBItemModel


class DBSite(DBItemModel):
    """Model representing a site in the database"""

    site_id: str
    longitude: Decimal
    latitude: Decimal
    acceptable_range: Decimal

    @staticmethod
    def item_type() -> ItemType:
        return ItemType.SITE

    @computed_field
    @property
    def pk(self) -> str:
        return self.item_type().value

    @computed_field
    @property
    def sk(self) -> str:
        return self.site_id

    def to_api_model(self) -> APISite:
        """The site as an API model, without the DB specific attributes"""
        return APISite(
            site_id=self.site_id,
            longitude=self.longitude,
            latitude=self.latitude,
            acceptable_range=self.acceptable_range,
        )
