from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_staff: bool = False

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        """Valide la robustesse du mot de passe."""
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        # Ajoutez d'autres validations de robustesse si nécessaire
        return v

class UserRead(UserBase):
    id: UUID
    is_active: bool
    
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_staff: Optional[bool] = None
    is_active: Optional[bool] = None
