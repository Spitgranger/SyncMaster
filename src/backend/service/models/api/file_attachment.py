"""
Representations of file attachments in the API
"""

from ..custom_base_model import CustomBaseModel


class APIFileAttachmentResponse(CustomBaseModel):
    """Format of a file attachment in an API response"""

    name: str
    url: str


class APIAddFileAttachment(CustomBaseModel):
    """Format of a request to add a file attachment to a site visit"""

    name: str
    s3_key: str


class APIRemoveFileAttachment(CustomBaseModel):
    """Format of a request to remove a file attachment from a site visit"""

    name: str
