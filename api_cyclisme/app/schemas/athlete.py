from pydantic import BaseModel, validator
from typing import Optional, List
from uuid import UUID

class AthleteBase(BaseModel):
    first_name: str
    last_name: str
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    vo2max: Optional[float] = None

    @validator('age')
    def age_range(cls, v):
        if v is not None and (v < 5 or v > 100):
            raise ValueError('L\'âge doit être compris entre 5 et 100 ans')
        return v

    @validator('weight')
    def weight_range(cls, v):
        if v is not None and (v < 20 or v > 250):
            raise ValueError('Le poids doit être compris entre 20 et 250 kg')
        return v

    @validator('height')
    def height_range(cls, v):
        if v is not None and (v < 100 or v > 250):
            raise ValueError('La taille doit être comprise entre 100 et 250 cm')
        return v

class AthleteCreate(AthleteBase):
    pass

class AthleteRead(AthleteBase):
    id: UUID
    user_id: UUID
    
    class Config:
        orm_mode = True

class AthleteUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    vo2max: Optional[float] = None