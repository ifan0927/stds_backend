from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from database import Base

class LeaveType(Base):
    __tablename__ = "leave_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # 假別名稱
    description = Column(Text)  # 假別描述
    is_active = Column(Boolean, default=True)  # 是否啟用
    created_at = Column(DateTime, server_default=func.now())
    
    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class LeaveApplication(Base):
    __tablename__ = "leave_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"))  # 關聯到假別表
    start_date = Column(DateTime)  # 請假開始時間（包含時分）
    end_date = Column(DateTime)    # 請假結束時間（包含時分）
    duration_hours = Column(Float)  # 請假時數
    reason = Column(Text)          # 請假原因
    status = Column(String(20), default="pending")  # pending, approved, rejected
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
