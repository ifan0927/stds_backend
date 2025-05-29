# schemas/file.py - 更新後的 Schema
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal, List
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
    sort_order: Optional[int] = 0  # 新增排序字段

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
    sort_order: Optional[int] = None  # 新增排序字段

class FileResponse(FileBase):
    id: int
    old_id: Optional[int] = None
    signed_url: Optional[str] = None
    url_expires_at: Optional[datetime] = None
    upload_time: datetime
    last_modified: datetime
    sort_order: int = 0  # 新增排序字段

    class Config:
        from_attributes = True

# Schema for file upload form
class FileUploadInfo(BaseModel):
    category: str
    ref_id: Optional[int] = None
    file_type: Literal["image", "document", "video", "audio", "other"] 
    file_info: Optional[str] = None
    sort_order: Optional[int] = None  # 新增排序字段

# 新增批量更新排序的 Schema
class FileSortUpdate(BaseModel):
    file_id: int
    sort_order: int

class FileSortUpdateRequest(BaseModel):
    file_orders: List[FileSortUpdate]