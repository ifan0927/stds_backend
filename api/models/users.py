from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "tenant"

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, nullable=True)
    name = Column(String(100))
    contact_info = Column(Text)
    id_number = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def model_update(self, update_data):
        for field, value in update_data.items():
            setattr(self, field, value)
        return self
       