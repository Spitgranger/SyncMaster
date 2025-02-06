"""
Defines the model for a document as represented in the database
"""

from pydantic import computed_field

from ...util import ItemType
from ..api.document import APIDocumentResponse
from .db_base import DBItemModel


class DBDocument(DBItemModel):
    """Model representing a document in the database"""

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

    def to_api_model(self) -> APIDocumentResponse:
        """The Document as an API model, without the DB specific attributes"""
        return APIDocumentResponse(
            site_id=self.site_id,
            document_path=self.document_path,
            requires_ack=self.requires_ack,
            last_modified=self.last_modified_time,
        )
