from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileBase(BaseModel):
    category: Optional[str] = None
    ref_id: Optional[int] = None
    file_type: Optional[str] = None
    filename: str
    original_filename: Optional[str] = None
    file_info: Optional[str] = None
    download_count: Optional[int] = 0
    uploader_id: Optional[int] = None

class FileCreate(FileBase):
    pass

class FileUpdate(BaseModel):
    category: Optional[str] = None
    ref_id: Optional[int] = None
    file_type: Optional[str] = None
    filename: Optional[str] = None
    original_filename: Optional[str] = None
    file_info: Optional[str] = None
    download_count: Optional[int] = None
    uploader_id: Optional[int] = None
    upload_time: Optional[datetime] = None

class File(FileBase):
    id: int
    old_id: Optional[int] = None
    upload_time: datetime

    class Config:
        from_attributes = True