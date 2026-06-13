# Pydantic schema
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Annotated
from pydantic.types import conint


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    owner_id: int

class PostResponse(BaseModel):
    title: str
    content: str
    published: bool
    owner_id: int
    owner: UserResponse

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int

class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(ge=0, le=1)] # not saved in db, only decides if vote to put or not
                                            # if value 1, put vote, if 0 delete vote, kind of indication


class PostOut(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        orm_mode = True