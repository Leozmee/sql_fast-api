import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import sqlite3
import datetime
from typing import List
from pydantic import BaseModel


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

def create_user_table():
    conn = sqlite3.connect("cyclist_database.db")
    cursor = conn.cursor()
    cursor.executescript(
        """
        DROP TABLE IF EXISTS User;
        CREATE TABLE User(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            is_staff BOOLEAN NOT NULL DEFAULT 0
        );
        """
    )
    conn.commit()
    conn.close()

def create_cyclistinfo_table():
    conn = sqlite3.connect("cyclist_database.db")
    cursor = conn.cursor()
    cursor.executescript(
        """
        DROP TABLE IF EXISTS Athlete;
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


def create_performance_table():
    conn = sqlite3.connect("cyclist_database.db")
    cursor = conn.cursor()
    cursor.executescript(
        """
        DROP TABLE IF EXISTS Performance;
        CREATE TABLE Performance(
            performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL, 
            time INTEGER NOT NULL,
            power REAL NOT NULL,
            oxygen INTEGER NOT NULL,
            cadence REAL NOT NULL,
            heart_rate REAL NOT NULL,
            respiration_frequency REAL NOT NULL,
            FOREIGN KEY(test_id) REFERENCES Test(test_id),
            FOREIGN KEY(user_id) REFERENCES User(id)
        );
        """
    )
    conn.commit()
    conn.close()

# -----------------------------
# MODELS
# -----------------------------

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    user_name: str
    email: str
    password: str

class AthletePerformance(BaseModel):
    test_id: int
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

def authenticate_user(email: str, password: str):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM User WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user if user and verify_password(password, user["password"]) else None

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
            "INSERT INTO User (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            (user.first_name, user.last_name, user.email, hashed_password)
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token_expires = datetime.timedelta(hours=1)
    access_token = create_access_token(data={"sub": user["email"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/add_performance")
def add_performance(performance: AthletePerformance, token: str = Depends(oauth2_scheme)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Performance (
            test_id, user_id, time, power,
            oxygen, cadence, heart_rate, respiration_frequency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            performance.test_id,
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
    conn.close()
    return {"message": "Performance added successfully"}

@app.get("/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {}
    stats["strongest_athlete"] = cursor.execute(
        "SELECT user_id FROM Performance ORDER BY power DESC LIMIT 1"
    ).fetchone()
    stats["highest_vo2max"] = cursor.execute(
        "SELECT user_id FROM CyclistInfo ORDER BY age DESC LIMIT 1"
    ).fetchone()
    stats["best_power_weight_ratio"] = cursor.execute(
        "SELECT Performance.user_id, MAX(power / weight) AS ratio FROM Performance INNER JOIN CyclistInfo ON Performance.user_id = CyclistInfo.user_id"
    ).fetchone()
    conn.close()
    return stats

@app.get("/")
async def root():
    return {"message": "Hello World"}

# -----------------------------
# INITIALIZE DATABASE (CALL ONCE)
# -----------------------------
def initialize_database():
    create_user_table()
    create_cyclistinfo_table()
    create_performance_table()
    # Optionally you can prepopulate the Test table here if needed.

@app.on_event("startup")
def startup_event():
    initialize_database()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("fastapi_app:app", host="127.0.0.1", port=8000, reload=True)