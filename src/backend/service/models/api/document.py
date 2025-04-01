"""
Module containg models to be used with the API
"""

from datetime import datetime
from typing import Optional

from ...util import FileType
from ..custom_base_model import CustomBaseModel


class APIDocumentResponse(CustomBaseModel):
    """A Document as represented in the API"""

    document_id: str
    document_name: str
    document_type: FileType
    parent_folder_id: str
    site_id: str
    document_path: str
    s3_presigned_get: Optional[str] = None
    requires_ack: bool
    last_modified: datetime
    document_expiry: Optional[datetime] = None


class APIDocumentListResponse(CustomBaseModel):
    """A List of documents as represented in the API"""

    document_id: list[APIDocumentResponse]


class APIDocumentUploadRequest(CustomBaseModel):
    """A Document upload request from API"""

    site_id: str
    document_name: str
    document_type: FileType
    parent_folder_id: str
    document_path: str
    s3_key: str
    e_tag: str
    user_id: str
    requires_ack: bool
    document_expiry: Optional[datetime] = None


class APIExpiringDocumentResponse(CustomBaseModel):
    """A list of expiring documents for the provided date delta"""

    documents: list[APIDocumentResponse]
    last_key: Optional[str] = None
