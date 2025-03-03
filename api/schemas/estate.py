from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EstateBase(BaseModel):
    title: str
    owner_name: str
    address: Optional[str] = None
    contact_info: Optional[str] = None
    facilities: Optional[str] = None
    utility_config: Optional[str] = None

class EstateCreate(EstateBase):
    pass

class EstateUpdate(BaseModel):
    title: Optional[str] = None
    owner_name: Optional[str] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    facilities: Optional[str] = None
    utility_config: Optional[str] = None

class Estate(EstateBase):
    id: int
    old_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
