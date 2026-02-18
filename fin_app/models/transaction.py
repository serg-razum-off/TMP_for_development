from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class Category(str, Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    HOUSING = "Housing"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"


class Transaction(BaseModel):
    id: int | None = None
    user_id: int
    amount: float
    description: str
    category: Category
    created: datetime | None = None
    updated: datetime | None = None
