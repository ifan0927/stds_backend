from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CheckoutRecordBase(BaseModel):
    rental_id: int
    room_id: int
    checkout_reason: str  # 退租原因：租約到期/提前解約/轉房
    checkout_date: datetime  # 退租日期
    final_electric_reading: Optional[float] = None  # 最終電錶讀數
    total_settlement_amount: float  # 總結算金額（正數=收費，負數=退費）
    notes: Optional[str] = None  # 備註

class CheckoutRecordCreate(CheckoutRecordBase):
    pass

class CheckoutRecordUpdate(BaseModel):
    checkout_reason: Optional[str] = None
    checkout_date: Optional[datetime] = None
    final_electric_reading: Optional[float] = None
    total_settlement_amount: Optional[float] = None
    notes: Optional[str] = None

class CheckoutRecord(CheckoutRecordBase):
    id: int
    recorder_id: Optional[int] = None
    recorder_name: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class CheckoutRequest(BaseModel):
    checkout_reason: str  # 退租原因：租約到期/提前解約/轉房
    checkout_date: datetime  # 退租日期
    final_electric_reading: Optional[float] = None  # 最終電錶讀數
    total_settlement_amount: float  # 總結算金額（正數=收費，負數=退費）
    notes: Optional[str] = None  # 備註

class CheckoutResponse(BaseModel):
    success: bool
    message: str
    rental_id: int
    room_id: int
    checkout_date: datetime
    settlement_amount: float
    checkout_record_id: int
    electric_record_id: Optional[int] = None
    accounting_record_id: Optional[int] = None