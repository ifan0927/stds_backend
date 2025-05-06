from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class AuthUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)  # Email (作為登入使用)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)        # 姓名
    nickname = Column(String(100), nullable=True)     # 暱稱
    group = Column(String(50), nullable=True)         # 群組
    job_title = Column(String(100), nullable=True)    # 職稱
    role = Column(String(20), default="staff")        # 權限: admin, manager, staff
    hire_date = Column(Date, nullable=True)           # 到職日
    leave_date = Column(Date, nullable=True)          # 離職日
    id_number = Column(String(20), nullable=True)     # 身分證字號
    birthday = Column(Date, nullable=True)            # 生日
    phone = Column(String(20), nullable=True)         # 電話
    address = Column(Text, nullable=True)             # 地址
    notes = Column(Text, nullable=True)               # 備註
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # 現有關聯
    schedules = relationship("Schedule", back_populates="user")
    schedule_replies = relationship("ScheduleReply", back_populates="user")
