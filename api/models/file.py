# models/file.py - 更新後的模型
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from database import Base

class Files(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, nullable=True)
    
    # File categorization
    category = Column(String(255), index=True)
    ref_id = Column(Integer, index=True, nullable=True)
    file_type = Column(Enum("image", "document", "video", "audio", "other"), index=True)
    
    # File metadata
    filename = Column(String(255))  # The unique filename in storage
    original_filename = Column(String(255))  # The original filename uploaded by user
    content_type = Column(String(255))  # MIME type
    file_size = Column(BigInteger, nullable=True)  # Size in bytes
    
    # GCP storage information
    blob_path = Column(String(512))  # Full path in GCP bucket
    signed_url = Column(Text, nullable=True)  # Signed URL (may expire)
    url_expires_at = Column(DateTime, nullable=True)  # When the signed URL expires
    
    # Additional info
    file_info = Column(Text, nullable=True)  # JSON or other metadata
    download_count = Column(Integer, default=0)
    sort_order = Column(Integer, default=0, nullable=False)  # 新增排序字段
    
    # User and timestamps
    uploader_id = Column(Integer, ForeignKey("users.id"))
    upload_time = Column(DateTime, server_default=func.now(), index=True)
    last_modified = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def model_update(self, update_data):
        for field, value in update_data.items():
            setattr(self, field, value)
        return self