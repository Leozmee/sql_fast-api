from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import sqlite3
from app.database import get_db_connection
from app.models.performance import AthletePerformance, PerformanceResponse, StatsResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/performances", tags=["performances"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_performance(performance: AthletePerformance, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO Performance (
                user_id, time, power,
                oxygen, cadence, heart_rate, respiration_frequency
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                performance.user_id,
                performance.time,
                performance.power,
                performance.oxygen,
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

@router.get("/stats", response_model=StatsResponse)
def get_stats(current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {}
    
    # Get strongest athlete
    strongest = cursor.execute(
        "SELECT user_id, MAX(power) as max_power FROM Performance GROUP BY user_id ORDER BY max_power DESC LIMIT 1"
    ).fetchone()
    stats["strongest_athlete"] = strongest["user_id"] if strongest else None
    
    # Get athlete with highest VO2max
    highest_vo2max = cursor.execute(
        "SELECT user_id, MAX(oxygen) as max_oxygen FROM Performance GROUP BY user_id ORDER BY max_oxygen DESC LIMIT 1"
    ).fetchone()
    stats["highest_vo2max"] = highest_vo2max["user_id"] if highest_vo2max else None
    
    # Get best power to weight ratio
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
    stats["best_power_weight_ratio"] = best_ratio["user_id"] if best_ratio else None
    
    conn.close()
    return stats

@router.get("/user/{user_id}", response_model=List[PerformanceResponse])
def get_user_performances(user_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    performances = conn.execute(
        "SELECT * FROM Performance WHERE user_id = ? ORDER BY time ASC", 
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(p) for p in performances] if performances else []