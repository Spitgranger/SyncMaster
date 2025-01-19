from typing import Optional

from .db_base import DatabaseBaseModel, KeySchema


class DBJob(DatabaseBaseModel):
    user_id: str
    job_type: str
    work_order: str
    description: str | None = None

    @staticmethod
    def key_schema(gsi: Optional[str] = None) -> KeySchema:
        match gsi:
            case None:
                return KeySchema(hash="WorkOrder")
            case "ListGSI":
                return KeySchema(hash="UserId", range="JobType")
            case _:
                raise TypeError(f"No GSI [{gsi}] for this model")
