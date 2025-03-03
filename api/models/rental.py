from sqlalchemy import Column, Integer, String, Text, Date, DECIMAL, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    deposit = Column(DECIMAL(10, 2))
    rental_info = Column(Text)
    status = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def model_update(self, update_data):
        for field, value in update_data.items():
            setattr(self, field, value)
        return self