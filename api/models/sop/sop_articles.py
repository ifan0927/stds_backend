from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Float, ForeignKey
from sqlalchemy.sql import func
from database import Base

class SopArticles(Base):
    __tablename__ = "sop_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    imbeded_content = Column(Text)
    category_id = Column(Integer, ForeignKey("sop_categories.id", ondelete="SET NULL"))
    parent_id = Column(Integer, ForeignKey("sop_articles.id", ondelete="SET NULL"))
    status= Column(Enum("draft", "published", "archived"))
    view_count = Column(Integer)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    def model_dump(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 
    
    def model_update(self, update_data):
        for field, value in update_data.items():
            setattr(self, field, value)
        return