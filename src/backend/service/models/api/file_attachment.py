"""
Representations of file attachments in the API
"""

from datetime import datetime

from ..custom_base_model import CustomBaseModel


class APIFileAttachmentResponse(CustomBaseModel):
    """Format of a file attachment in an API response"""

    name: str
    url: str


class APIAddFileAttachment(CustomBaseModel):
    """Format of a request to add a file attachment to a site visit"""

    user_id: str
    site_id: str
    entry_time: datetime
    name: str
    url: str
