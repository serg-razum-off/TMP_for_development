from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    email: str
    created: datetime
    updated: datetime
