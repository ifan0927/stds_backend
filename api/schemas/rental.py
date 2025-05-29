from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import json

# New class to represent the JSON data in rental_info
class RentalInfoDetails(BaseModel):
    money: Optional[str] = None
    early_checkin: Optional[str] = None  
    initial_electric: Optional[float] = None

class RentalBase(BaseModel):
    old_id: Optional[int] = None
    room_id: int
    start_date: date
    end_date: Optional[date] = None
    deposit: Optional[float] = None
    rental_info: Optional[str] = None
    status: Optional[str] = None
    
    def get_rental_info_details(self) -> Optional[RentalInfoDetails]:
        if self.rental_info:
            try:
                info_dict = json.loads(self.rental_info)
                return RentalInfoDetails(**info_dict)
            except json.JSONDecodeError:
                return None
        return None

class RentalCreate(RentalBase):
    pass

class RentalUpdate(RentalBase):
    pass

class Rental(RentalBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# You might also want a response model that includes the parsed details
class RentalResponse(Rental):
    rental_info_details: Optional[RentalInfoDetails] = None