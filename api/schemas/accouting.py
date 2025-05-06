from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AccountingBase(BaseModel):
    old_id: Optional[int] = None
    title: str
    income: float
    date: datetime
    estate_id: Optional[int] = None
    rental_id: Optional[int] = None
    accounting_tag: Optional[str] = None
    payment_method: Optional[str] = None
    recorder_id: Optional[int] = None
    recorder_name: Optional[str] = None

class AccountingCreate(AccountingBase):
    pass

class AccountingUpdate(BaseModel):
    old_id: Optional[int] = None
    title: Optional[str] = None
    income: Optional[float] = None
    date: Optional[datetime] = None
    estate_id: Optional[int] = None
    rental_id: Optional[int] = None
    accounting_tag: Optional[str] = None
    payment_method: Optional[str] = None
    recorder_id: Optional[int] = None
    recorder_name: Optional[str] = None

class Accounting(AccountingBase):
    id: int

    class Config:
        orm_mode = True