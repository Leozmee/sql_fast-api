from sqlalchemy import Column, String, Boolean
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4, UUID
import bcrypt

if TYPE_CHECKING:
    from app.models.athlete import Athlete

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column("email", String, nullable=False, unique=True, index=True))
    hashed_password: str = Field(sa_column=Column("hashed_password", String, nullable=False))
    is_staff: bool = Field(default=False)
    is_active: bool = Field(default=True)
    first_name: Optional[str] = Field(default=None, sa_column=Column("first_name", String))
    last_name: Optional[str] = Field(default=None, sa_column=Column("last_name", String))
    username: Optional[str] = Field(default=None, sa_column=Column("username", String))
    
    
    athletes: List["Athlete"] = Relationship(back_populates="user")

    def verify_password(self, password: str) -> bool:
        """Vérifie si le mot de passe fourni correspond au mot de passe haché stocké."""
        return bcrypt.checkpw(password.encode(), self.hashed_password.encode())

    @staticmethod
    def hash_password(password: str) -> str:
        """Hache un mot de passe donné en utilisant bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()