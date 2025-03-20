from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    user_name: str
    email: str
    password: str
    is_staff: str = Field(default="NO")

    @validator('is_staff')
    def validate_is_staff(cls, v):
        if v.upper() not in ["YES", "NO"]:
            raise ValueError('is_staff must be either "YES" or "NO"')
        return v.upper()

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    user_name: str
    email: str
    is_staff: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str = None

