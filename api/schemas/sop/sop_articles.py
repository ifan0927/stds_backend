from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SopArticlesBase(BaseModel):
    title : str
    content : str
    imbeded_content : Optional[str] = None
    category_id : Optional[int] = None
    parent_id : Optional[int] = None
    status : str
    view_count : int
    created_by : Optional[int] = None
    updated_at : Optional[datetime] = None

class SopArticlesCreate(SopArticlesBase):
    status: str = "draft"
    view_count: int = 0

class SopArticlesUpdate(SopArticlesBase):
    title : Optional[str] = None
    content : Optional[str] = None
    imbeded_content : Optional[str] = None
    category_id : Optional[int] = None
    parent_id : Optional[int] = None
    status : Optional[str] = None
    view_count : Optional[int] = None
    created_by : Optional[int] = None
    updated_at : Optional[datetime] = None

class SopArticles(SopArticlesBase):
    id : int
    created_at : datetime