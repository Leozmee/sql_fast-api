from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.db.database import Base

class PerformanceData(Base):
    __tablename__ = "performance_data"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    test_id = Column(String(36), ForeignKey("tests.id"), nullable=False)
    time = Column(Integer, nullable=False)
    power = Column(Float, nullable=False)
    oxygen = Column(Float, nullable=False)
    cadence = Column(Float, nullable=False)
    heart_rate = Column(Float, nullable=False)
    respiration_freq = Column(Float, nullable=False)
    
    
    test = relationship("Test", back_populates="performance_data")