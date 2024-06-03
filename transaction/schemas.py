from pydantic import BaseModel
from typing import Optional, List


from enum import Enum

class TransactionType(Enum):
    Single=""
    Course="MENTOR"

class Transaction(BaseModel):
    type: str
    course_id: Optional[str]
    