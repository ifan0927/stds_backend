from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, ForeignKey
from sqlalchemy.sql import func 
from database import Base

class Room(Base):
    __tablename__ = "rooms" 

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, nullable=True)
    estate_id = Column(Integer, ForeignKey("estates.id"))
    room_number = Column(String(50), nullable=False)
    floor = Column(String(50))
    size = Column(DECIMAL(10, 2))
    facilities = Column(Text)
    price_info = Column(Text)
    zone = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    