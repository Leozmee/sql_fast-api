from fastapi import APIRouter, Depends, HTTPException, status
import sqlite3
from app.database import get_db_connection
from app.models.athlete import AthleteCreate, AthleteResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/athletes", tags=["athletes"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_athlete(athlete: AthleteCreate, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Athlete (user_id, gender, age, weight, height) VALUES (?, ?, ?, ?, ?)",
            (athlete.user_id, athlete.gender, athlete.age, athlete.weight, athlete.height)
        )
        conn.commit()
        return {"message": "Athlete added successfully"}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="User ID already exists or not valid") from e
    finally:
        conn.close()

@router.get("/{user_id}", response_model=AthleteResponse)
def get_athlete(user_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    athlete = conn.execute("SELECT * FROM Athlete WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    
    if athlete is None:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    return dict(athlete)