from pydantic import BaseModel, validator
from typing import Optional, List
from uuid import UUID
from datetime import date
from enum import Enum

class TestTypeEnum(str, Enum):
    INCREMENTAL = "incremental"
    WINGATE = "wingate"
    PROTOCOL_1 = "protocol_1"
    PROTOCOL_2 = "protocol_2"

class TestBase(BaseModel):
    test_type: TestTypeEnum
    test_date: Optional[date] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    
    # Champs calculés optionnels (lors de la création)
    max_power: Optional[float] = None
    avg_power: Optional[float] = None
    power_weight_ratio: Optional[float] = None
    vo2max: Optional[float] = None
    max_hr: Optional[int] = None
    avg_hr: Optional[int] = None
    total_work: Optional[float] = None
    test_duration: Optional[int] = None
    
    notes: Optional[str] = None

class TestCreate(TestBase):
    athlete_id: UUID

class TestRead(TestBase):
    id: UUID
    athlete_id: UUID
    
    class Config:
        orm_mode = True

class TestUpdate(BaseModel):
    test_type: Optional[TestTypeEnum] = None
    test_date: Optional[date] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    max_power: Optional[float] = None
    avg_power: Optional[float] = None
    power_weight_ratio: Optional[float] = None
    vo2max: Optional[float] = None
    max_hr: Optional[int] = None
    avg_hr: Optional[int] = None
    total_work: Optional[float] = None
    test_duration: Optional[int] = None
    notes: Optional[str] = None

# Schéma pour les statistiques de test
class TestStats(BaseModel):
    test_id: UUID
    athlete_id: UUID
    athlete_name: str
    test_type: str
    test_date: date
    max_power: Optional[float] = None
    avg_power: Optional[float] = None
    power_weight_ratio: Optional[float] = None
    vo2max: Optional[float] = None
    
    class Config:
        orm_mode = True