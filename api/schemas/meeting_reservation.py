from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from .meeting_room import MeetingRoom  # 假設 MeetingRoom 定義在這個模組中

class MeetingReservationBase(BaseModel):
    room_id: int
    title: str
    note: Optional[str] = None
    start_time: datetime
    end_time: datetime

    @validator('start_time', 'end_time')
    def validate_time_precision(cls, v):
        # 檢查時間必須是整點或半點
        if v.minute not in [0, 30] or v.second != 0 or v.microsecond != 0:
            raise ValueError('時間必須是整點或半點（如 09:00, 09:30）')
        return v

    @validator('end_time')
    def validate_end_time(cls, v, values):
        # 檢查結束時間必須大於開始時間
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('結束時間必須晚於開始時間')
        return v

class MeetingReservationCreate(MeetingReservationBase):
    pass

class MeetingReservationUpdate(BaseModel):
    title: Optional[str] = None
    note: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @validator('start_time', 'end_time')
    def validate_time_precision(cls, v):
        if v is not None:
            if v.minute not in [0, 30] or v.second != 0 or v.microsecond != 0:
                raise ValueError('時間必須是整點或半點（如 09:00, 09:30）')
        return v

class MeetingReservationResponse(MeetingReservationBase):
    id: int
    created_by_id: int
    created_by_name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    room: MeetingRoom

    class Config:
        from_attributes = True

class MeetingReservationSimple(BaseModel):
    """簡化版本，不包含 room 關聯資訊"""
    id: int
    room_id: int
    title: str
    note: Optional[str] = None
    start_time: datetime
    end_time: datetime
    created_by_id: int
    created_by_name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True