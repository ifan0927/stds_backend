from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EntryTableBase(BaseModel):
    type : Optional[str] = None
    title : str
    content : str
    created_by : Optional[str] = None
    

class EntryTableCreate(EntryTableBase):
    pass

class EntryTableUpdate(EntryTableBase):
    type : Optional[str] = None
    title : Optional[str] = None
    content : Optional[str] = None
    created_by : Optional[str] = None
    created_at : Optional[datetime] = None

class EntryTable(EntryTableBase):
    id : int
    created_at : datetime



