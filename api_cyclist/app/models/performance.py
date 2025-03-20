from pydantic import BaseModel
from typing import Optional

class AthletePerformance(BaseModel):
    user_id: int
    time: int
    power: float
    vo2_max:float
    oxygen: int
    cadence: float
    heart_rate: float
    respiration_frequency: float

class PerformanceResponse(BaseModel):
    performance_id: int
    user_id: int
    time: int
    power: float
    vo2_max:float
    oxygen: int
    cadence: float
    heart_rate: float
    respiration_frequency: float

class StatsResponse(BaseModel):
    strongest_athlete: int = None
    highest_vo2max: int = None
    best_power_weight_ratio: int = None

class StatsResponseWithNames(BaseModel):
    strongest_athlete: Optional[str] = None
    highest_vo2max: Optional[str] = None
    best_power_weight_ratio: Optional[str] = None