from pydantic import BaseModel
from enum import Enum

class USER_ROLES(Enum):
    STUDENT="STUDENT"
    MENTOR="MENTOR"


class User(BaseModel):
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True