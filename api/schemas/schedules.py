from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScheduleBase(BaseModel):
    estate_id: Optional[int] = None
    room_id: Optional[int] = None
    event_date: Optional[datetime] = None
    event_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    estate_id: Optional[int] = None
    room_id: Optional[int] = None
    event_date: Optional[datetime] = None
    event_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Schedule(ScheduleBase):
    id: int
    old_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True