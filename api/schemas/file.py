from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal
from datetime import datetime

class FileBase(BaseModel):
    category: Optional[str] = None
    ref_id: Optional[int] = None
    file_type: Optional[Literal["image", "document", "video", "audio", "other"]] = None
    filename: str
    original_filename: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    blob_path: Optional[str] = None
    file_info: Optional[str] = None
    download_count: Optional[int] = 0
    uploader_id: Optional[int] = None

class FileCreate(FileBase):
    pass

class FileUpdate(BaseModel):
    category: Optional[str] = None
    ref_id: Optional[int] = None
    file_type: Optional[Literal["image", "document", "video", "audio", "other"]] = None
    filename: Optional[str] = None
    original_filename: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    blob_path: Optional[str] = None
    file_info: Optional[str] = None
    download_count: Optional[int] = None
    uploader_id: Optional[int] = None
    upload_time: Optional[datetime] = None
    last_modified: Optional[datetime] = None

class FileResponse(FileBase):
    id: int
    old_id: Optional[int] = None
    signed_url: Optional[str] = None
    url_expires_at: Optional[datetime] = None
    upload_time: datetime
    last_modified: datetime

    class Config:
        from_attributes = True

# Schema for file upload form
class FileUploadInfo(BaseModel):
    category: str
    ref_id: Optional[int] = None
    file_type: Literal["image", "document", "video", "audio", "other"] 
    file_info: Optional[str] = None