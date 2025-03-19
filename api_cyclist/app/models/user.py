from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    user_name: str
    email: str
    password: str

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