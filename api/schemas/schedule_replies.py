from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScheduleReplyBase(BaseModel):
    schedule_id: int
    content: str

class ScheduleReplyCreate(ScheduleReplyBase):
    pass

class ScheduleReplyUpdate(BaseModel):
    content: Optional[str] = None

class ScheduleReply(ScheduleReplyBase):
    id: int
    user_id: int
    created_at: datetime
    user_name: Optional[str] = None  # 用於返回用戶名

    class Config:
        from_attributes = True