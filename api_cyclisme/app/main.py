# main.py (version mise à jour)
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.db.database import create_db_and_tables
from app.routes import auth
from app.routes.athletes import router as athletes_router
from app.routes.tests import router as tests_router, performance_router
from app.routes.stats import router as stats_router  # Nouvelles routes pour les statistiques
from app.routes.users import router as users_router

# Création de l'application FastAPI
app = FastAPI(
    title="API de Gestion des Performances Cyclistes",
    description="API pour suivre et analyser les performances d'athlètes cyclistes",
    version="0.1.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À ajuster en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(auth.router)
app.include_router(users_router)
app.include_router(athletes_router)
app.include_router(tests_router)
app.include_router(performance_router)
app.include_router(stats_router)  # Nouvelles routes de statistiques

@app.on_event("startup")
def on_startup():
    """
    Actions à effectuer au démarrage de l'application.
    """
    create_db_and_tables()

@app.get("/")
def read_root():
    """
    Page d'accueil de l'API.
    """
    return {
        "message": "Bienvenue sur l'API de Gestion des Performances Cyclistes",
        "documentation": "/docs",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    # Démarrage du serveur en mode développement
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)