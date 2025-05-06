from sqlalchemy import Column, Integer, String, Text, Date, DECIMAL, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("tenant.id"))  # 修改為關聯到tenant表
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
    
    accountings = relationship("Accounting", back_populates="rental")
    room = relationship("Room", back_populates="rentals")
    user = relationship("User", backref="rentals", foreign_keys=[user_id])  # 修改為明確的外鍵引用