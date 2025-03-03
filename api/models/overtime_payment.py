from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey
from sqlalchemy.sql import func
from database import Base

class OvertimePayment(Base):
    __tablename__ = "overtime_payment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    duration = Column(Float)
    reason = Column(Text)
    status = Column(String(20), default="pending")
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_note = Column(Text)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def model_update(self, update_data):
        for field, value in update_data.items():
            setattr(self, field, value)
        return