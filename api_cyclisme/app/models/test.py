from sqlalchemy import Column, String, Float, Date, Text, Integer
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import uuid4, UUID
from datetime import date
import enum


from app.models.athlete import Athlete
from app.models.performance_data import PerformanceData


class TestType(str, enum.Enum):
    INCREMENTAL = "incremental"
    WINGATE = "wingate"
    PROTOCOL_1 = "protocol_1"
    PROTOCOL_2 = "protocol_2"


class Test(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    athlete_id: UUID = Field(foreign_key="athlete.id")
    test_type: str = Field()  
    test_date: date = Field(default=date.today())
    weight: Optional[float] = Field(default=None, sa_column=Column("weight", Float))
    height: Optional[float] = Field(default=None, sa_column=Column("height", Float))
    
    # Métriques de performance
    max_power: Optional[float] = Field(default=None, sa_column=Column("max_power", Float))
    avg_power: Optional[float] = Field(default=None, sa_column=Column("avg_power", Float))
    power_weight_ratio: Optional[float] = Field(default=None, sa_column=Column("power_weight_ratio", Float))
    
    # Métriques respiratoires
    vo2max: Optional[float] = Field(default=None, sa_column=Column("vo2max", Float))
    max_hr: Optional[int] = Field(default=None, sa_column=Column("max_hr", Integer))
    avg_hr: Optional[int] = Field(default=None, sa_column=Column("avg_hr", Integer))
    
    # Métriques supplémentaires pour l'analyse
    total_work: Optional[float] = Field(default=None, sa_column=Column("total_work", Float))  # Travail total en joules
    test_duration: Optional[int] = Field(default=None, sa_column=Column("test_duration", Integer))  # Durée en secondes
    
    notes: Optional[str] = Field(default=None, sa_column=Column("notes", Text))
    
    # Relations
    athlete: "Athlete" = Relationship(back_populates="tests")
    performance_data: List["PerformanceData"] = Relationship(back_populates="test")
    
    def calculate_metrics(self, db_session):
        """
        Calcule les métriques de performance à partir des données brutes.
        Cette méthode doit être appelée après l'import des données de performance.
        """
        from sqlalchemy import func
        from app.models.performance_data import PerformanceData
        
        # Requête pour récupérer les statistiques sur les données de performance
        query = db_session.query(
            func.max(PerformanceData.power).label("max_power"),
            func.avg(PerformanceData.power).label("avg_power"),
            func.max(PerformanceData.heart_rate).label("max_hr"),
            func.avg(PerformanceData.heart_rate).label("avg_hr"),
            func.max(PerformanceData.time).label("max_time")
        ).filter(PerformanceData.test_id == self.id)
        
        result = query.first()
        
        if result:
            # Mise à jour des métriques de base
            self.max_power = result.max_power
            self.avg_power = result.avg_power
            self.max_hr = int(result.max_hr) if result.max_hr else None
            self.avg_hr = int(result.avg_hr) if result.avg_hr else None
            self.test_duration = result.max_time
            
            # Calcul du rapport puissance/poids
            if self.avg_power and self.weight and self.weight > 0:
                self.power_weight_ratio = self.avg_power / self.weight
            
            # Calcul du travail total (puissance moyenne * durée)
            if self.avg_power and self.test_duration:
                self.total_work = self.avg_power * self.test_duration
            
            # Pour le VO2max, on peut utiliser la valeur maximale si elle est mesurée directement
            oxygen_query = db_session.query(
                func.max(PerformanceData.oxygen).label("max_oxygen")
            ).filter(PerformanceData.test_id == self.id)
            
            oxygen_result = oxygen_query.first()
            if oxygen_result and oxygen_result.max_oxygen:
                self.vo2max = oxygen_result.max_oxygen
                
            # Enregistrer les changements
            db_session.add(self)
            db_session.commit()
            
        return self