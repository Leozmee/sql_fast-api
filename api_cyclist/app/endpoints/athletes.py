from fastapi import APIRouter, Depends, HTTPException, status
import sqlite3
from app.database import get_db_connection
from app.models.athlete import AthleteCreate, AthleteResponse, AthleteUpdate
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

@router.put("/{user_id}", response_model=AthleteResponse)
def update_athlete(user_id: int, athlete: AthleteUpdate, current_user = Depends(get_current_user)):
    # Vérifier si l'athlète existe
    conn = get_db_connection()
    existing_athlete = conn.execute("SELECT * FROM Athlete WHERE user_id = ?", (user_id,)).fetchone()
    
    if existing_athlete is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    # Mise à jour de l'athlète
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Athlete 
            SET gender = ?, age = ?, weight = ?, height = ?
            WHERE user_id = ?
            """,
            (athlete.gender, athlete.age, athlete.weight, athlete.height, user_id)
        )
        conn.commit()
        
        # Récupérer l'athlète mis à jour
        updated_athlete = conn.execute("SELECT * FROM Athlete WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        
        return dict(updated_athlete)
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_athlete(user_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    
    # Vérifier si l'athlète existe
    existing_athlete = conn.execute("SELECT * FROM Athlete WHERE user_id = ?", (user_id,)).fetchone()
    
    if existing_athlete is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Athlete WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return None
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e