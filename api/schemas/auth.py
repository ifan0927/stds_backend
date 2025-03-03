# schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None

class AuthUserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    nickname: Optional[str] = None
    group: Optional[str] = None
    job_title: Optional[str] = None
    role: str = "host"  # 預設為一般工作人員
    hire_date: Optional[date] = None
    leave_date: Optional[date] = None
    id_number: Optional[str] = None
    birthday: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class AuthUserUpdate(BaseModel):
    password: Optional[str] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    group: Optional[str] = None
    job_title: Optional[str] = None
    role: Optional[str] = None
    hire_date: Optional[date] = None
    leave_date: Optional[date] = None
    email: Optional[EmailStr] = None
    id_number: Optional[str] = None
    birthday: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class AuthUser(BaseModel):
    id: int
    email: str
    name: str
    nickname: Optional[str] = None
    group: Optional[str] = None
    job_title: Optional[str] = None
    role: str
    hire_date: Optional[date] = None
    leave_date: Optional[date] = None
    email: Optional[str] = None
    id_number: Optional[str] = None
    birthday: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenRefresh(BaseModel):
    refresh_token: str