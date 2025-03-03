from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class OvertimePaymentBase(BaseModel):
    user_id: Optional[int] = None
    date: date
    duration: float
    reason: str
    status: Optional[str] = "pending"
    approved_by: Optional[int] = None
    approved_note : Optional[str] = None
    approved_at: Optional[datetime] = None

class OvertimePaymentCreate(OvertimePaymentBase):
    pass

class OvertimePaymentUpdate(OvertimePaymentBase):
    user_id: Optional[int] = None
    date: Optional[datetime] = None
    duration: Optional[float] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    approved_by: Optional[int] = None
    approved_note: Optional[str] = None
    approved_at: Optional[datetime] = None

class OvertimePayment(OvertimePaymentBase):
    id: int
    created_at: datetime
