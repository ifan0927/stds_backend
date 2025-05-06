from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .schedule_replies import ScheduleReply

class ScheduleBase(BaseModel):
    estate_id: Optional[int] = None
    room_id: Optional[int] = None
    event_date: Optional[datetime] = None
    event_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[int] = None  # 新增: 創建者ID

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    estate_id: Optional[int] = None
    room_id: Optional[int] = None
    event_date: Optional[datetime] = None
    event_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[int] = None

class Schedule(ScheduleBase):
    id: int
    old_id: Optional[int] = None
    created_at: datetime
    user_name: Optional[str] = None  # 用於返回用戶名
    
    class Config:
        from_attributes = True

class ScheduleWithReplies(Schedule):
    replies: List[ScheduleReply] = []