from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.db.database import Base

class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    vo2max = Column(Float, nullable=True)
    
   
    user = relationship("User", back_populates="athletes")
    tests = relationship("Test", back_populates="athlete", cascade="all, delete-orphan")