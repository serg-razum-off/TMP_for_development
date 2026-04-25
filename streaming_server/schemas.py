from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderDraft(BaseModel):
    user_id: int
    created_by_id: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "created_by_id": 6,
                "comment": "New order draft from mobile agent",
            }
        }
