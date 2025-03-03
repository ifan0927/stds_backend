from pydantic import BaseModel
from typing import Optional 
from datetime import datetime

class RoomBase(BaseModel):
    room_number: str
    floor: Optional[str] = None
    size: Optional[float] = None
    facilities: Optional[str] = None
    price_info: Optional[str] = None
    zone: Optional[str] = None
    

class RoomCreate(RoomBase):
    estate_id: int

class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    floor: Optional[str] = None
    size: Optional[float] = None
    facilities: Optional[str] = None
    price_info: Optional[str] = None
    zone: Optional[str] = None

class Room(RoomBase):
    id: int
    old_id: Optional[int] = None
    estate_id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True