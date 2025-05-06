from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    old_id = Column(Integer, nullable=True)
    estate_id = Column(Integer, nullable=True)
    room_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 新增: 記錄創建者
    event_date = Column(DateTime, nullable=True)
    event_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(tz))
    
    # 關聯
    replies = relationship("ScheduleReply", back_populates="schedule")
    user = relationship("AuthUser", back_populates="schedules")

class ScheduleReply(Base):
    __tablename__ = "schedule_replies"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(tz))
    
    # 關聯
    schedule = relationship("Schedule", back_populates="replies")
    user = relationship("AuthUser", back_populates="schedule_replies")