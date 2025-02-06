"""
Module containg models to be used with the API
"""

from datetime import datetime

from ..custom_base_model import CustomBaseModel


class APIDocumentResponse(CustomBaseModel):
    """A Document as represented in the API"""

    site_id: str
    document_path: str
    s3_presigned_get: str = ""
    requires_ack: bool
    last_modified: datetime


class APIDocumentUploadRequest(CustomBaseModel):
    """A Document upload request from API"""

    site_id: str
    document_path: str
    s3_key: str
    e_tag: str
    user_id: str
    requires_ack: bool
