from sqlalchemy import Column, String, Float, Integer
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4, UUID

if TYPE_CHECKING:
    from app.models.test import Test
    from app.models.user import User


class Athlete(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    first_name: str = Field(sa_column=Column("first_name", String, nullable=False))
    last_name: str = Field(sa_column=Column("last_name", String, nullable=False))
    age: Optional[int] = Field(default=None, sa_column=Column("age", Integer))
    weight: Optional[float] = Field(default=None, sa_column=Column("weight", Float))
    height: Optional[float] = Field(default=None, sa_column=Column("height", Float))
    vo2max: Optional[float] = Field(default=None, sa_column=Column("vo2max", Float))
    
    
    
    user: "User" = Relationship(back_populates="athletes")
    tests: List["Test"] = Relationship(back_populates="athlete")