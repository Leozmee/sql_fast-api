# app/models/test.py
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum
from datetime import date

from app.db.database import Base

class TestType(str, enum.Enum):
    INCREMENTAL = "incremental"
    WINGATE = "wingate"
    PROTOCOL_1 = "protocol_1"
    PROTOCOL_2 = "protocol_2"

class Test(Base):
    __tablename__ = "tests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    athlete_id = Column(String(36), ForeignKey("athletes.id"), nullable=False)
    test_type = Column(String, nullable=False)
    test_date = Column(Date, nullable=False, default=date.today)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    
    max_power = Column(Float, nullable=True)
    avg_power = Column(Float, nullable=True)
    power_weight_ratio = Column(Float, nullable=True)
    
    vo2max = Column(Float, nullable=True)
    max_hr = Column(Integer, nullable=True)
    avg_hr = Column(Integer, nullable=True)
    
    total_work = Column(Float, nullable=True)
    test_duration = Column(Integer, nullable=True)
    
    notes = Column(Text, nullable=True)
    

    athlete = relationship("Athlete", back_populates="tests")
    performance_data = relationship("PerformanceData", back_populates="test", cascade="all, delete-orphan")
    
    def calculate_metrics(self, db_session):
        """
        Calcule les métriques de performance à partir des données brutes.
        """
        from sqlalchemy import func
        from app.models.performance_data import PerformanceData
        
        max_power = db_session.query(func.max(PerformanceData.power)).filter(PerformanceData.test_id == self.id).scalar()
        avg_power = db_session.query(func.avg(PerformanceData.power)).filter(PerformanceData.test_id == self.id).scalar()
        max_hr = db_session.query(func.max(PerformanceData.heart_rate)).filter(PerformanceData.test_id == self.id).scalar()
        avg_hr = db_session.query(func.avg(PerformanceData.heart_rate)).filter(PerformanceData.test_id == self.id).scalar()
        max_time = db_session.query(func.max(PerformanceData.time)).filter(PerformanceData.test_id == self.id).scalar()
        
        self.max_power = max_power
        self.avg_power = avg_power
        self.max_hr = int(max_hr) if max_hr else None
        self.avg_hr = int(avg_hr) if avg_hr else None
        self.test_duration = max_time
        
        # Calcul du rapport puissance/poids
        if self.avg_power and self.weight and self.weight > 0:
            self.power_weight_ratio = self.avg_power / self.weight
        
        # Calcul du travail total
        if self.avg_power and self.test_duration:
            self.total_work = self.avg_power * self.test_duration
        
        # Pour le VO2max
        max_oxygen = db_session.query(func.max(PerformanceData.oxygen)).filter(PerformanceData.test_id == self.id).scalar()
        if max_oxygen:
            self.vo2max = max_oxygen
        
        # Enregistrer les changements
        db_session.add(self)
        db_session.commit()
        
        return self