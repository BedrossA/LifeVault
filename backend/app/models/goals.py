from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
