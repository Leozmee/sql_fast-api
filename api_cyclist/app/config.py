import os
from pydantic import BaseModel

class Settings(BaseModel):
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "cyclist_database.db"

settings = Settings()