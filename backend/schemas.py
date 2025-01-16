from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: Optional[str]
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None
