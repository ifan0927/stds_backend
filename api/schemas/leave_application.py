from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class LeaveTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class LeaveTypeCreate(LeaveTypeBase):
    pass

class LeaveTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class LeaveType(LeaveTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class LeaveApplicationBase(BaseModel):
    user_id: Optional[int] = None
    leave_type_id: int
    start_date: datetime
    end_date: datetime
    duration_hours: float
    reason: str
    status: Optional[str] = "pending"
    approved_by: Optional[int] = None
    approved_note: Optional[str] = None
    approved_at: Optional[datetime] = None

    @validator('duration_hours')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('請假時數必須大於0')
        return v
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('結束時間必須晚於開始時間')
        return v

class LeaveApplicationCreate(LeaveApplicationBase):
    pass

class LeaveApplicationUpdate(BaseModel):
    user_id: Optional[int] = None
    leave_type_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_hours: Optional[float] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    approved_by: Optional[int] = None
    approved_note: Optional[str] = None
    approved_at: Optional[datetime] = None

class LeaveApplication(LeaveApplicationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True