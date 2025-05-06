from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ElectricRecordBase(BaseModel):
    room_id: int
    reading: float
    record_year: int
    record_month: int
    recorder_id: Optional[int] = None

class ElectricRecordCreate(ElectricRecordBase):
    pass

class ElectricRecordUpdate(BaseModel):
    room_id: Optional[int] = None
    reading: Optional[float] = None
    record_year: Optional[int] = None
    record_month: Optional[int] = None
    recorder_id: Optional[int] = None

class ElectricRecord(ElectricRecordBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True