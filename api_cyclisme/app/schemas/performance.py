from pydantic import BaseModel, validator
from typing import Optional, List
from uuid import UUID

class PerformanceDataBase(BaseModel):
    time: int
    power: float
    oxygen: float
    cadence: float
    heart_rate: float
    respiration_freq: float
    
    @validator('time')
    def time_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Le temps doit être positif')
        return v
        
    @validator('power', 'oxygen', 'cadence', 'heart_rate', 'respiration_freq')
    def values_must_be_positive(cls, v, values, **kwargs):
        if v < 0:
            raise ValueError('Les valeurs physiologiques doivent être positives')
        return v

class PerformanceDataCreate(PerformanceDataBase):
    test_id: UUID

class PerformanceDataRead(PerformanceDataBase):
    id: UUID
    test_id: UUID
    
    class Config:
        orm_mode = True

class PerformanceDataUpdate(BaseModel):
    time: Optional[int] = None
    power: Optional[float] = None
    oxygen: Optional[float] = None
    cadence: Optional[float] = None
    heart_rate: Optional[float] = None
    respiration_freq: Optional[float] = None

# Schémas pour les analyses et les statistiques
class PerformanceStats(BaseModel):
    max_power: float
    avg_power: float
    max_hr: int
    avg_hr: int
    max_oxygen: float
    avg_oxygen: float
    total_duration: int  # en secondes
    
    class Config:
        orm_mode = True

class PerformanceTimePoint(BaseModel):
    time: int
    power: float
    oxygen: float
    heart_rate: float
    
    class Config:
        orm_mode = True

class PerformanceTimeSeries(BaseModel):
    test_id: UUID
    athlete_id: UUID
    test_type: str
    data_points: List[PerformanceTimePoint]
    
    class Config:
        orm_mode = True