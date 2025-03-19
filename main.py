import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import sqlite3
import datetime
from typing import List
from pydantic import BaseModel
import jwt
import os


SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

# -----------------------------
# DATABASE HELPERS & SETUP
# -----------------------------

def get_db_connection():
    conn = sqlite3.connect("cyclist_database.db")
    conn.row_factory = sqlite3.Row
    return conn

def check_table_exists(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def create_user_table():
    if not check_table_exists("User"):
        conn = sqlite3.connect("cyclist_database.db")
        cursor = conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE User(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                is_staff BOOLEAN NOT NULL DEFAULT 0
            );
            """
        )
        conn.commit()
        conn.close()
    print("User table set up successfully")

def create_cyclistinfo_table():
    if not check_table_exists("Athlete"):
        conn = sqlite3.connect("cyclist_database.db")
        cursor = conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE Athlete(
                user_id INTEGER PRIMARY KEY,
                gender TEXT CHECK(gender IN ('male', 'female')) NOT NULL,
                age INTEGER CHECK(age > 0) NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                FOREIGN KEY(user_id) REFERENCES User(id)
            );
            """
        )
        conn.commit()
        conn.close()
    print("Athlete table set up successfully")

def create_performance_table():
    if not check_table_exists("Performance"):
        conn = sqlite3.connect("cyclist_database.db")
        cursor = conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE Performance(
                performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL, 
                time INTEGER NOT NULL,
                power REAL NOT NULL,
                oxygen INTEGER NOT NULL,
                cadence REAL NOT NULL,
                heart_rate REAL NOT NULL,
                respiration_frequency REAL NOT NULL,
                FOREIGN KEY(user_id) REFERENCES User(id)
            );
            """
        )
        conn.commit()
        conn.close()
    print("Performance table set up successfully")

# -----------------------------
# MODELS
# -----------------------------

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    user_name: str
    email: str
    password: str

class AthleteCreate(BaseModel):
    user_id: int
    gender: str
    age: int
    weight: float
    height: float

class AthletePerformance(BaseModel):
    user_id: int
    time: int
    power: float
    oxygen: int
    cadence: float
    heart_rate: float
    respiration_frequency: float

# -----------------------------
# AUTH UTILITIES
# -----------------------------
def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    # Check if username is an email
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM User WHERE email = ?", (username,)).fetchone()
    conn.close()
    
    if user and verify_password(password, user["password"]):
        return user
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM User WHERE email = ?", (email,)).fetchone()
    conn.close()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# -----------------------------
# API ENDPOINTS
# -----------------------------
@app.post("/register")
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

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = datetime.timedelta(hours=1)
    access_token = create_access_token(data={"sub": user["email"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/add_athlete")
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

@app.post("/add_performance")
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

@app.get("/stats")
def get_stats(current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {}
    
    # Get strongest athlete
    strongest = cursor.execute(
        "SELECT user_id, MAX(power) as max_power FROM Performance GROUP BY user_id ORDER BY max_power DESC LIMIT 1"
    ).fetchone()
    stats["strongest_athlete"] = strongest["user_id"] if strongest else None
    
    # Get athlete with highest VO2max (changed from age to oxygen)
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

@app.get("/user_performances/{user_id}")
def get_user_performances(user_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    performances = conn.execute(
        "SELECT * FROM Performance WHERE user_id = ? ORDER BY time ASC", 
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(p) for p in performances] if performances else []

@app.get("/")
async def root():
    return {"message": "Cyclist Performance API"}

# -----------------------------
# INITIALIZE DATABASE (CALL ONCE)
# -----------------------------
def initialize_database():
    create_user_table()
    create_cyclistinfo_table()
    create_performance_table()

# Option to reset database
def reset_database():
    if os.path.exists("cyclist_database.db"):
        os.remove("cyclist_database.db")
    initialize_database()

@app.on_event("startup")
def startup_event():
    initialize_database()

if __name__ == '__main__':
    import uvicorn
    
    # Uncomment the line below if you want to reset the database
    # reset_database()
    
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)