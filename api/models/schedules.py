from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, nullable=True)
    estate_id = Column(Integer, ForeignKey("estates.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    event_date = Column(DateTime)
    event_type = Column(String(50))
    description = Column(Text)
    status = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def model_update(self, update_data):
        for field, value in update_data.items():
            setattr(self, field, value)
        return