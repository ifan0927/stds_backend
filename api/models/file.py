from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, nullable=True)
    category = Column(String(255))
    ref_id = Column(Integer)
    file_type = Column(Enum("image", "document"))
    filename = Column(String(255))
    original_filename = Column(String(255))
    file_info = Column(Text)
    download_count = Column(Integer, default=0)
    uploader_id = Column(Integer, ForeignKey("users.id"))
    upload_time = Column(DateTime, server_default=func.now())

    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def model_update(self, update_data):
        for field, value in update_data.items():
            setattr(self, field, value)
        return