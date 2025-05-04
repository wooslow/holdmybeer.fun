from datetime import datetime

from pydantic import BaseModel


class UserBaseSchema(BaseModel):
    id: int
    email: str
    permissions: int

    class Config:
        from_attributes = True


class UserRegisterSchema(BaseModel):
    email: str
    password: str


class UserTokensSchema(BaseModel):
    access_token: str
    refresh_token: str


class UserLoginSchema(BaseModel):
    email: str
    password: str
