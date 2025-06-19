from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MeetingRoomBase(BaseModel):
    name: str
    location: str

class MeetingRoomCreate(MeetingRoomBase):
    pass

class MeetingRoomUpdate(MeetingRoomBase):
    name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

class MeetingRoom(MeetingRoomBase):
    id: int
    is_active: bool
    created_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True