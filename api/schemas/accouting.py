from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AccountingBase(BaseModel):
    old_id: Optional[int]
    title: str
    income: float
    date: datetime
    estate_id: Optional[int]
    rental_id: Optional[int]
    accounting_tag: Optional[str]

class AccountingCreate(AccountingBase):
    pass

class AccountingUpdate(AccountingBase):
    pass

class AccountingInDBBase(AccountingBase):
    id: int

    class Config:
        orm_mode: True

class Accounting(AccountingInDBBase):
    pass

class AccountingInDB(AccountingInDBBase):
    pass