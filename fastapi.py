import fastapi as FastAPI
import sqlite3
import pandas as pd
import bcrypt

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

