from datetime import datetime

from ..custom_base_model import CustomBaseModel


class APIFileAttachment(CustomBaseModel):
    name: str
    url: str


class APIAddFileAttachment(CustomBaseModel):
    user_id: str
    site_id: str
    entry_time: datetime
    name: str
    url: str
