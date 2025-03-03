from sqlalchemy import Column, Integer, Float, DateTime, func
from database import Base

class ElectricRecord(Base):
    __tablename__ = "electric_records"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, nullable=False)
    reading = Column(Float, nullable=False)
    record_year = Column(Integer, nullable=False)
    record_month = Column(Integer, nullable=False)
    recorder_id = Column(Integer, nullable=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())