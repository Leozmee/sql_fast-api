import sqlite3
import os
from app.config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.DATABASE_URL)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")  # Activer les contraintes de clé étrangère
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
        conn = get_db_connection()
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

def create_athlete_table():
    if not check_table_exists("Athlete"):
        conn = get_db_connection()
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE Performance(
                performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL, 
                time INTEGER NOT NULL,
                power  NOT NULL,
                vo2_max REAL NOT NULL,
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

def initialize_database():
    create_user_table()
    create_athlete_table()
    create_performance_table()

def reset_database():
    if os.path.exists(settings.DATABASE_URL):
        os.remove(settings.DATABASE_URL)
    initialize_database()