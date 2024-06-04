from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

class USER_ROLES(str, Enum):
    STUDENT = "STUDENT"
    MENTOR = "MENTOR"

class UserBase(BaseModel):
    username: str
    role: USER_ROLES

class User(UserBase):
    username: str

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    title: str
    content: str

class QuestionCreate(QuestionBase):
    owner: Optional[str] = None

class Question(QuestionBase):
    id: int
    owner: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

class AnswerBase(BaseModel):
    content: str

class AnswerCreate(AnswerBase):
    question_id: int
    owner: Optional[str] = None

class Answer(AnswerBase):
    id: int
    question_id: int
    owner: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    answer_id: int
    owner: Optional[str] = None

class Comment(CommentBase):
    id: int
    answer_id: int
    owner: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
