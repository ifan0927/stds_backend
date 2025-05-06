from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class ElectricRecord(Base):
    __tablename__ = "electric_records"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    reading = Column(Float, nullable=False)
    record_year = Column(Integer, nullable=False)
    record_month = Column(Integer, nullable=False)
    recorder_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 關聯到AuthUser
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    room = relationship("Room", back_populates="electric_records")
    recorder = relationship("AuthUser", foreign_keys=[recorder_id])  # 修改為關聯AuthUser