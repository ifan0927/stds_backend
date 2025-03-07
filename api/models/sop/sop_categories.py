from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey
from sqlalchemy.sql import func
from database import Base

class SopCategories(Base):
    __tablename__ = "sop_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 
    
    def model_update(self, update_data):
        for field, value in update_data.items():
            setattr(self, field, value)
        return