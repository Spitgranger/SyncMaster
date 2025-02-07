"""
Defines structure of a site visit in the API
"""

from datetime import datetime
from typing import Optional

from ..custom_base_model import CustomBaseModel


class APISiteVisit(CustomBaseModel):
    """A site visit as represented in the API"""

    site_id: str
    user_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
