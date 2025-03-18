from sqlalchemy import Column, Float, Integer
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.test import Test


class PerformanceData(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    test_id: UUID = Field(foreign_key="test.id")
    time: int = Field(sa_column=Column("time", Integer, nullable=False))
    power: float = Field(sa_column=Column("power", Float, nullable=False))
    oxygen: float = Field(sa_column=Column("oxygen", Float, nullable=False))
    cadence: float = Field(sa_column=Column("cadence", Float, nullable=False))
    heart_rate: float = Field(sa_column=Column("heart_rate", Float, nullable=False))
    respiration_freq: float = Field(sa_column=Column("respiration_freq", Float, nullable=False))
    
   
    test: "Test" = Relationship(back_populates="performance_data")