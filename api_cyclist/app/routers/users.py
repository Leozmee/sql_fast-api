from fastapi import APIRouter, Depends, HTTPException, status
import sqlite3
from app.database import get_db_connection
from app.models.user import UserCreate, UserResponse
from app.utils.security import hash_password, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(user.password)
    try:
        cursor.execute(
            "INSERT INTO User (user_name, first_name, last_name, email, password) VALUES (?, ?, ?, ?, ?)",
            (user.user_name, user.first_name, user.last_name, user.email, hashed_password)
        )
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already exists") from e
    finally:
        conn.close()

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user = Depends(get_current_user)):
    return dict(current_user)