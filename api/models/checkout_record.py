from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class CheckoutRecord(Base):
    __tablename__ = "checkout_records"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    checkout_reason = Column(String(100), nullable=False)  # 退租原因
    checkout_date = Column(DateTime, nullable=False, index=True)  # 退租日期
    final_electric_reading = Column(Float, nullable=True)  # 最終電錶讀數
    total_settlement_amount = Column(Float, nullable=False, default=0)  # 總結算金額
    notes = Column(Text, nullable=True)  # 備註
    recorder_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 記錄人
    recorder_name = Column(String(100), nullable=True)  # 記錄人名稱
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 關聯關係
    rental = relationship("Rental", backref="checkout_record")
    room = relationship("Room", backref="checkout_records")