import pydantic
class CourseFromUser(pydantic.BaseModel):
    id: int
    class Config:
        from_attributes = True

class Course(pydantic.BaseModel):
    id: int
    creator: str
    class Config:
        from_attributes = True