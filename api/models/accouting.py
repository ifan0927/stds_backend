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
