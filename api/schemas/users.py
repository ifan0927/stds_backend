from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    contact_info: Optional[str] = None
    id_number: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    id_number: Optional[str] = None

class User(UserBase):
    id: int
    old_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True