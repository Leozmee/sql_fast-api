from sqlmodel import Session, SQLModel, create_engine
from typing import Generator
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "cyclist_database.db")
DB_URL = f"sqlite:///{DB_PATH}"


engine = create_engine(
    DB_URL, 
    connect_args={"check_same_thread": False},  
    echo=True  
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()