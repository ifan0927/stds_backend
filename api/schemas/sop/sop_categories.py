from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SopCategoriesBase(BaseModel):
    name : str
    description : Optional[str] = None
    updated_at : Optional[datetime] = None

class SopCategoriesCreate(SopCategoriesBase):
    pass

class SopCategoriesUpdate(SopCategoriesBase):
    name : Optional[str] = None
    description : Optional[str] = None
    updated_at : Optional[datetime] = None

class SopCategories(SopCategoriesBase):
    id : int
    created_at : datetime