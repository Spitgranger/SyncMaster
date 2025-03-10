"""
Defines the model for a document as represented in the database
"""

from datetime import datetime
from typing import Optional

from pydantic import computed_field

from ...util import FileType, ItemType
from ..api.document import APIDocumentResponse
from .db_base import DBItemModel


class DBDocument(DBItemModel):
    """Model representing a document in the database"""

    document_name: str  # Will be name of file, including extensions (e.g. "test.pdf")
    document_type: FileType  # Either "file" or "folder"
    document_id: str  # Unique identifier to the file or folder
    document_expiry: Optional[datetime] = None

    # Folder structure property
    parent_folder_id: str  # The parent folder of the file. Root or folder name

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
        return f"{self.item_type().value}#{self.site_id}#{self.parent_folder_id}"

    @computed_field
    @property
    def sk(self) -> str:
        """
        SK is the document_id, this is done to prevent ambiguities in the case
        that both the document has nested documents of the same name
        """
        return self.document_id

    def to_api_model(self, s3_link: Optional[str] = None) -> APIDocumentResponse:
        """
        The Document as an API model, without the DB specific attributes
        :param s3_link: The s3 presigned url
        """
        return APIDocumentResponse(
            document_id=self.document_id,
            document_name=self.document_name,
            document_type=self.document_type,
            site_id=self.site_id,
            document_path=self.document_path,
            requires_ack=self.requires_ack,
            last_modified=self.last_modified_time,
            s3_presigned_get=s3_link,
            document_expiry=self.document_expiry,
            parent_folder_id=self.parent_folder_id,
        )
