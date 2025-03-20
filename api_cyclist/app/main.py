from fastapi import FastAPI
from app.database import initialize_database
from app.endpoints import auth, users, athletes, performances

app = FastAPI(title="Cyclist Performance API")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(athletes.router)
app.include_router(performances.router)

@app.on_event("startup")
def startup_event():
    initialize_database()

@app.get("/")
async def root():
    return {"message": "Cyclist Performance API"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)