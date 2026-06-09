# Pydantic schema
from pydantic import BaseModel

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostResponse(BaseModel):
    title: str
    content: str
    published: bool

    class Config:
        from_attributes = True
