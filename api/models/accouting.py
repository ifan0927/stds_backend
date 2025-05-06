from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Accounting(Base):
    __tablename__ = "accounting"

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, index=True)
    title = Column(String(255), index=True)
    income = Column(Float, index=True)
    date = Column(DateTime, index=True)
    estate_id = Column(Integer, ForeignKey("estates.id"), index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), index=True)
    accounting_tag = Column(String(255), index=True)
    payment_method = Column(String(50), index=True)  # 新增繳納方式欄位
    recorder_id = Column(Integer, ForeignKey("users.id"), index=True)  # 關聯到AuthUser
    recorder_name = Column(String(100))  # 新增記錄人名稱

    # 修正關聯關係 - 使用back_populates而非backref
    estate = relationship("Estate", back_populates="accountings") 
    rental = relationship("Rental", back_populates="accountings")
    # 不定義對AuthUser的關聯，避免複雜循環引用