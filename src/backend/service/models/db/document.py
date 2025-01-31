from .db_base import DBItemModel
from pydantic import computed_field

class DBDocument(DBItemModel):
    document_path: str
    s3_bucket: str
    s3_key: str
    s3_e_tag: str
    requires_ack: bool = True
    site_id: str = "ALL"

    @staticmethod
    @property
    def item_type() -> str:
        return "Document"

    @computed_field
    @property
    def pk(self) -> str:
        return f"{self.item_type}#{self.site_id}"
    
    @computed_field
    @property
    def sk(self) -> str:
        return self.document_path
