from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from database import Base

class EntryTable(Base):
    __tablename__ = "entry_table"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum("system", "bug", "fixed"))
    title = Column(String(255))
    content = Column(String(255))
    created_by = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def model_update(self, update_data):
        for field, value in update_data.items():
            setattr(self, field, value)
        return
    