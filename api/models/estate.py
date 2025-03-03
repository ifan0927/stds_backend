from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Estate(Base):
    __tablename__ = "estates"

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, nullable=True)
    title = Column(String(255), nullable=False)
    owner_name = Column(String(100), nullable=False)
    address = Column(String(255))
    contact_info = Column(Text)
    facilities = Column(Text)
    utility_config = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())