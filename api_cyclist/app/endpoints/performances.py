from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import sqlite3
from app.database import get_db_connection
from app.models.performance import AthletePerformance, PerformanceResponse, StatsResponse, StatsResponseWithNames
from app.utils.security import get_current_user, get_current_staff_user

router = APIRouter(prefix="/performances", tags=["performances"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_performance(performance: AthletePerformance, current_user = Depends(get_current_staff_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Performance (
                user_id, time, power, 
                vo2_max, oxygen, cadence, heart_rate, respiration_frequency
            ) VALUES (?, ?, ?, ?, ?, ?, ? ,?)
            """,
            (
                performance.user_id,
                performance.time,
                performance.power,
                performance.oxygen,
                performance.vo2_max,
                performance.cadence,
                performance.heart_rate,
                performance.respiration_frequency
            )
        )
        conn.commit()
        return {"message": "Performance added successfully"}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Invalid user_id") from e
    finally:
        conn.close()

@router.get("/stats", response_model=StatsResponseWithNames)
def get_stats_with_names(current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {}
    
    def get_username(user_id):
        """ Récupère le nom d'utilisateur à partir d'un user_id. """
        user = conn.execute("SELECT user_name FROM User WHERE id = ?", (user_id,)).fetchone()
        return user["user_name"] if user else None
    
    strongest = cursor.execute(
        "SELECT user_id, MAX(power) as max_power FROM Performance GROUP BY user_id ORDER BY max_power DESC LIMIT 1"
    ).fetchone()
    stats["strongest_athlete"] = get_username(strongest["user_id"]) if strongest else None
    
    highest_vo2max = cursor.execute(
        "SELECT user_id, MAX(oxygen) as max_oxygen FROM Performance GROUP BY user_id ORDER BY max_oxygen DESC LIMIT 1"
    ).fetchone()
    stats["highest_vo2max"] = get_username(highest_vo2max["user_id"]) if highest_vo2max else None
    
    best_ratio = cursor.execute(
        """
        SELECT Performance.user_id, MAX(Performance.power / Athlete.weight) AS ratio 
        FROM Performance 
        INNER JOIN Athlete ON Performance.user_id = Athlete.user_id
        GROUP BY Performance.user_id
        ORDER BY ratio DESC
        LIMIT 1
        """
    ).fetchone()
    stats["best_power_weight_ratio"] = get_username(best_ratio["user_id"]) if best_ratio else None
    
    conn.close()
    return stats


@router.get("/user/{user_id}", response_model=List[PerformanceResponse])
def get_user_performances(user_id: int, current_user = Depends(get_current_staff_user)):
    conn = get_db_connection()
    performances = conn.execute(
        "SELECT * FROM Performance WHERE user_id = ? ORDER BY time ASC", 
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(p) for p in performances] if performances else []

@router.patch("/{performance_id}")
async def update_performance(performance_id: int, performance: AthletePerformance, current_user: dict = Depends(get_current_staff_user)):
    print(current_user)
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE Performance SET power = ?, heart_rate = ?, vo2_max = ?, respiration_frequency = ?, cadence = ?
            WHERE performance_id = ? AND user_id = ?
            """,
            (performance.power, performance.heart_rate, performance.vo2_max, performance.respiration_frequency, performance.cadence, performance_id, current_user['id'])
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Performance not found or you don't have permission to update")
        
        return {"message": "Performance updated successfully"}

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
    finally:
        conn.close()

@router.delete("/{performance_id}")
async def delete_performance(performance_id: int, current_user: dict = Depends(get_current_staff_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM Performance WHERE performance_id = ? AND user_id = ?", (performance_id, current_user['id'])
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Performance not found or you don't have permission to delete")

        return {"message": "Performance deleted successfully"}

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e
    finally:
        conn.close()

@router.get("/my-stats", response_model=List[PerformanceResponse])
def get_user_performances(current_user = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_db_connection()
    performances = conn.execute(
        "SELECT * FROM Performance WHERE user_id = ? ORDER BY time ASC", 
        (user_id,)
    ).fetchall()
    conn.close()
    
    if not performances:
        return []
        
    return [dict(p) for p in performances]


@router.get("/all_users")
def get_all_users():
    """Récupère tous les utilisateurs pour déboguer"""
    conn = get_db_connection()
    try:
        users = conn.execute("SELECT id, user_name, first_name, last_name FROM User").fetchall()
        conn.close()
        return [{"id": u["id"], "user_name": u["user_name"], 
                "name": f"{u['first_name']} {u['last_name']}"} for u in users]
    except Exception as e:
        conn.close()
        return {"error": str(e)}


@router.get("/user_name/{user_name}", response_model=List[PerformanceResponse])
def get_user_performances_by_username(user_name: str, current_user=Depends(get_current_staff_user)):
    conn = get_db_connection()
    
    user = conn.execute(
        "SELECT id FROM User WHERE user_name = ?",
        (user_name,)
    ).fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user_id = user["id"]

    performances = conn.execute(
        "SELECT * FROM Performance WHERE user_id = ? ORDER BY time ASC",
        (user_id,)
    ).fetchall()
    
    conn.close()

    return [dict(p) for p in performances] if performances else []
