"""
Defines the model for a document as represented in the database
"""

from pydantic import computed_field

from ...util import ItemType
from .db_base import DBItemModel


class DBDocument(DBItemModel):
    document_path: str
    s3_bucket: str
    s3_key: str
    s3_e_tag: str
    requires_ack: bool = True
    site_id: str = "ALL"

    @staticmethod
    def item_type() -> ItemType:
        return ItemType.DOCUMENT

    @computed_field
    @property
    def pk(self) -> str:
        return f"{self.item_type().value}#{self.site_id}"

    @computed_field
    @property
    def sk(self) -> str:
        return self.document_path
