from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class RentalBase(BaseModel):
    old_id: Optional[int] = None
    room_id: int
    user_id: int
    start_date: date
    end_date: Optional[date] = None
    deposit: Optional[float] = None
    rental_info: Optional[str] = None
    status: Optional[str] = None

class RentalCreate(RentalBase):
    pass

class RentalUpdate(RentalBase):
    pass

class Rental(RentalBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True